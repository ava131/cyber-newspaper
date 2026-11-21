import fcntl
import hashlib
import json
import smtplib
import ssl
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mail_delivery import ROOT, MailError, check_auth, load_config, prepare, receipt, receipt_path, send, store_password


class MailDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.edition = "2026-11-21"
        (self.root / "config").mkdir()
        (self.root / "config/mail.json").write_bytes((ROOT / "config/mail.example.json").read_bytes())
        self.config = load_config(self.root)
        self.password = "abcdefghijklmnop"
        edition = self.root / "data/editions" / self.edition
        edition.mkdir(parents=True)
        (edition / "editorial.json").write_bytes((ROOT / "data/editions" / self.edition / "editorial.json").read_bytes())
        (edition / "provenance.json").write_text(json.dumps({"edition":self.edition,"pages":6}))
        (self.root / f"cyber-daily-{self.edition}.html").write_text("<!doctype html><p>六版报纸测试附件</p>")
        self.clients = []

    def factory(self, auth_error=False, data_error=None, quit_error=False):
        parent = self

        class FakeSMTP:
            def __init__(self,host,port,timeout,context):
                parent.assertEqual((host,port),("smtp.qq.com",465))
                parent.assertTrue(context.check_hostname)
                parent.assertEqual(context.verify_mode,ssl.CERT_REQUIRED)
                self.data_calls = 0
                parent.clients.append(self)

            def ehlo(self):
                return 250, b"ok"

            def login(self,username,password):
                parent.assertEqual(username,parent.config["sender"])
                parent.assertEqual(password,parent.password)
                if auth_error:
                    raise smtplib.SMTPAuthenticationError(535,parent.password.encode())

            def send_message(self,message,from_addr,to_addrs):
                self.data_calls += 1
                parent.assertEqual(from_addr,parent.config["sender"])
                parent.assertEqual(to_addrs,parent.config["recipients"])
                if data_error:
                    raise data_error
                return {}

            def quit(self):
                if quit_error:
                    raise smtplib.SMTPServerDisconnected("lost after acceptance")

            def close(self):
                pass

        return FakeSMTP

    def test_mime_round_trip_and_attachment_integrity(self):
        _, manifest = prepare(self.edition,self.config,self.root)
        data = (self.root / "data/editions" / self.edition / "mail/message.eml").read_bytes()
        message = BytesParser(policy=policy.default).parsebytes(data)
        self.assertEqual(message["To"],self.config["recipients"][0])
        self.assertEqual(message["From"].addresses[0].addr_spec,self.config["sender"])
        self.assertIn(self.edition,message["Subject"])
        self.assertEqual(message.get_body(preferencelist=("html",)).get_content_type(),"text/html")
        attachments = list(message.iter_attachments())
        self.assertEqual(len(attachments),1)
        self.assertEqual(hashlib.sha256(attachments[0].get_payload(decode=True)).hexdigest(),manifest["attachment_sha256"])
        self.assertFalse(receipt_path(self.edition,self.config,self.root).exists())

    def test_account_check_does_not_send_data(self):
        check_auth(self.config,self.password,self.factory())
        self.assertEqual(self.clients[0].data_calls,0)

    def test_success_and_quit_disconnect_still_prevent_duplicates(self):
        first = send(self.edition,self.config,self.root,self.password,self.factory(quit_error=True))
        second = send(self.edition,self.config,self.root,self.password,self.factory())
        self.assertEqual(first["status"],"accepted")
        self.assertEqual(second["message_id"],first["message_id"])
        self.assertEqual(len(self.clients),1)
        self.assertEqual(self.clients[0].data_calls,1)

    def test_auth_failure_is_known_and_redacts_credentials(self):
        with self.assertRaises(MailError) as error:
            send(self.edition,self.config,self.root,self.password,self.factory(auth_error=True))
        self.assertEqual(error.exception.code,"auth_rejected")
        state = receipt(self.edition,self.config,self.root)
        self.assertEqual(state["status"],"failed")
        self.assertNotIn(self.password,json.dumps(state)+str(error.exception))
        self.assertEqual(self.clients[0].data_calls,0)

    def test_disconnect_during_data_is_unknown_and_blocks_retry(self):
        with self.assertRaises(MailError):
            send(self.edition,self.config,self.root,self.password,self.factory(data_error=smtplib.SMTPServerDisconnected("lost during data")))
        self.assertEqual(receipt(self.edition,self.config,self.root)["status"],"unknown")
        with self.assertRaises(MailError):
            send(self.edition,self.config,self.root,self.password,self.factory())
        self.assertEqual(len(self.clients),1)

    def test_explicit_rejection_can_be_retried(self):
        with self.assertRaises(MailError):
            send(self.edition,self.config,self.root,self.password,self.factory(data_error=smtplib.SMTPDataError(554,b"rejected")))
        self.assertEqual(receipt(self.edition,self.config,self.root)["status"],"failed")
        result = send(self.edition,self.config,self.root,self.password,self.factory())
        self.assertEqual(result["status"],"accepted")

    def test_parallel_send_is_blocked_before_connecting(self):
        path = receipt_path(self.edition,self.config,self.root)
        path.parent.mkdir(parents=True)
        with (path.parent / ".send.lock").open("a") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(MailError) as error:
                send(self.edition,self.config,self.root,self.password,self.factory())
        self.assertEqual(error.exception.code,"busy")
        self.assertEqual(len(self.clients),0)

    def test_password_never_appears_in_process_arguments(self):
        calls = []

        def run(arguments,**kwargs):
            calls.append((arguments,kwargs))
            return SimpleNamespace(returncode=0,stdout=b"",stderr=b"")

        with patch("mail_delivery.subprocess.run",side_effect=run),patch("mail_delivery.read_password",return_value=self.password):
            store_password(self.config,self.password)
        self.assertNotIn(self.password,json.dumps(calls[0][0]))
        self.assertIn(self.password.encode(),calls[0][1]["input"])


if __name__ == "__main__":
    unittest.main()
