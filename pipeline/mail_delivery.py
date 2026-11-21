import argparse
import fcntl
import hashlib
import hmac
import html
import json
import os
import re
import shlex
import smtplib
import ssl
import subprocess
import tempfile
from datetime import datetime
from email import policy
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ZoneInfo("Asia/Shanghai")


class MailError(Exception):
    def __init__(self, message, code="mail_error"):
        super().__init__(message)
        self.code = code


def load_config(root=ROOT):
    config = json.loads((root / "config/mail.json").read_text())
    addresses = [config["sender"], *config["recipients"]]
    if not config["recipients"] or any(not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", address) for address in addresses):
        raise MailError("发件或收件地址格式不正确。", "config")
    if config["smtp_host"] != "smtp.qq.com" or config["smtp_port"] != 465 or config["security"] != "ssl":
        raise MailError("当前发送模块使用QQ邮箱的加密发信配置。", "config")
    return config


def private_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".mail-")
    try:
        with os.fdopen(descriptor, "w") as file:
            json.dump(value, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_password(value):
    password = "".join(value.split())
    if not re.fullmatch(r"[A-Za-z0-9]{12,64}", password):
        raise MailError("请粘贴QQ邮箱生成的客户端授权码，通常为16位字母。", "credential_format")
    return password


def credential_present(config):
    result = subprocess.run(["/usr/bin/security", "find-generic-password", "-a", config["sender"], "-s", config["keychain_service"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
    return result.returncode == 0


def read_password(config):
    try:
        result = subprocess.run(["/usr/bin/security", "find-generic-password", "-a", config["sender"], "-s", config["keychain_service"], "-w"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=45)
    except (OSError, subprocess.TimeoutExpired):
        raise MailError("未能读取本机钥匙串，请在配置页重新保存授权码。", "keychain") from None
    if result.returncode:
        raise MailError("尚未配置QQ邮箱授权码，请先打开本机配置页。", "missing_credential")
    return validate_password(result.stdout.decode().rstrip("\r\n"))


def store_password(config, value):
    password = validate_password(value)
    command = shlex.join(["add-generic-password", "-U", "-a", config["sender"], "-s", config["keychain_service"], "-w", password]) + "\n"
    try:
        result = subprocess.run(["/usr/bin/security", "-i"], input=command.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        if result.returncode or not hmac.compare_digest(read_password(config), password):
            raise MailError("钥匙串保存未完成，请允许系统提示后重试。", "keychain")
    except (OSError, subprocess.TimeoutExpired):
        raise MailError("钥匙串保存未完成，请允许系统提示后重试。", "keychain") from None


def receipt_path(edition, config, root=ROOT):
    key = hashlib.sha256(json.dumps([edition, config["sender"], sorted(config["recipients"])], separators=(",", ":")).encode()).hexdigest()[:20]
    return root / ".local/mail/receipts" / (edition + "-" + key + ".json")


def receipt(edition, config, root=ROOT):
    path = receipt_path(edition, config, root)
    return json.loads(path.read_text()) if path.exists() else {"edition":edition, "status":"not_sent"}


def digest_html(editorial, weather, edition):
    escape = html.escape
    weather_html = ""
    if weather:
        current, today = weather["current"], weather["forecast"][0]
        weather_html = f'<tr><td style="padding:18px 24px;border-bottom:1px solid #c9bfaa;background:#eae2cd"><b>{escape(weather["location"])}</b>　{escape(today["condition"])}　{today["low"]:g}—{today["high"]:g}℃<br><span style="font-size:12px;color:#655e50">{current["time"][11:16]}预报 · {escape(current["wind_direction"])}风 {current["wind_kmh"]:g} km/h · 降水概率{today["rain_probability"]:g}% · {escape(weather["tip"])}</span></td></tr>'
    pages = {page["id"]:page for page in editorial["pages"]}
    stories = []
    for spread in editorial["spreads"]:
        page = pages[spread["pages"][0]]
        secondary = ""
        if len(spread["pages"]) > 1:
            other = pages[spread["pages"][1]]
            secondary = f'<p style="font-size:13px;line-height:1.7;margin:14px 0 0;color:#76624b">另一版：{escape(other["headline"].replace(chr(10),""))}</p>'
        stories.append(f'<tr><td style="padding:24px;border-bottom:1px solid #c9bfaa"><p style="color:#8b312b;font-size:12px;margin:0 0 10px">{escape(spread["label"])}</p><h2 style="font-family:Songti SC,STSong,serif;font-size:25px;line-height:1.4;margin:0 0 13px">{escape(page["headline"].replace(chr(10),""))}</h2><p style="font-size:15px;line-height:1.9;margin:0">{escape(page["deck"])}</p>{secondary}</td></tr>')
    title = f'赛博日报 · {edition}'
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title></head><body style="margin:0;padding:24px 10px;background:#e4dfd3;color:#25241f;font-family:PingFang SC,Arial,sans-serif"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center"><table role="presentation" width="620" cellspacing="0" cellpadding="0" style="width:100%;max-width:620px;background:#f4efdf;border:1px solid #c9bfaa"><tr><td style="padding:28px 24px 22px;border-bottom:4px double #25241f"><h1 style="font-family:Songti SC,STSong,serif;font-size:38px;letter-spacing:5px;margin:0 0 9px">赛博日报</h1><span style="font-size:12px;color:#6d6659">'+edition+' · '+escape(editorial.get("issue_label","日报"))+' · 四栏目六版</span></td></tr>'+weather_html+''.join(stories)+'<tr><td style="padding:22px 24px;font-size:13px;line-height:1.9;color:#6d6659"><b>完整报纸见HTML附件。</b><br>下载附件后用浏览器打开，可翻页、查看原画及来源账单。<br>本邮件由你配置的赛博日报投递程序发送。</td></tr></table></td></tr></table></body></html>'


def prepare(edition, config=None, root=ROOT):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", edition):
        raise MailError("请指定有效的报纸日期。", "edition")
    datetime.strptime(edition, "%Y-%m-%d")
    config = config or load_config(root)
    folder = root / "data/editions" / edition
    artifact = root / f"cyber-daily-{edition}.html"
    if not artifact.exists() or artifact.resolve().parent != root.resolve():
        raise MailError("没有找到这一天的完整报纸。", "artifact")
    provenance = json.loads((folder / "provenance.json").read_text())
    editorial = json.loads((folder / "editorial.json").read_text())
    if provenance["edition"] != edition or provenance["pages"] != 6:
        raise MailError("当期报纸与来源记录不匹配。", "artifact")
    weather_path = folder / "weather.json"
    weather = json.loads(weather_path.read_text()) if weather_path.exists() else None
    body = digest_html(editorial, weather, edition)
    plain = f"赛博日报 · {edition}\n\n" + "\n\n".join(page["label"]+"："+page["headline"].replace("\n","")+"\n"+page["deck"] for page in editorial["pages"] if page["id"] in ("politics","finance","technology","culture")) + "\n\n完整报纸见HTML附件，下载后用浏览器打开。\n"
    subject = f"赛博日报｜{edition} · {editorial.get('issue_label','日报')}"
    previous = receipt(edition, config, root)
    message = EmailMessage(policy=policy.SMTP)
    username, domain = config["sender"].split("@",1)
    message["From"] = Address(config["sender_name"], username, domain)
    message["To"] = ", ".join(config["recipients"])
    message["Subject"] = subject
    message["Date"] = format_datetime(datetime.now(LOCAL))
    message["Message-ID"] = previous.get("message_id") or make_msgid(domain=domain)
    message["X-Cyber-Daily-Edition"] = edition
    message.set_content(plain)
    message.add_alternative(body, subtype="html")
    attachment = artifact.read_bytes()
    message.add_attachment(attachment, maintype="text", subtype="html", filename=artifact.name)
    out = folder / "mail"
    out.mkdir(exist_ok=True)
    (out / "preview.html").write_text(body)
    (out / "preview.txt").write_text(plain)
    (out / "message.eml").write_bytes(message.as_bytes())
    manifest = {"edition":edition,"sender":config["sender"],"recipients":config["recipients"],"subject":subject,"message_id":str(message["Message-ID"]),
                "attachment":artifact.name,"attachment_bytes":len(attachment),"attachment_sha256":hashlib.sha256(attachment).hexdigest(),"eml_bytes":(out/"message.eml").stat().st_size,
                "prepared_at":datetime.now(LOCAL).isoformat(),"preview_path":str(out/"preview.html")}
    (out / "manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return message, manifest


def smtp_error(error, during_data=False):
    if isinstance(error,smtplib.SMTPAuthenticationError):
        return MailError("QQ登录未通过，请检查IMAP/SMTP服务和客户端授权码。", "auth_rejected")
    if isinstance(error,smtplib.SMTPRecipientsRefused):
        return MailError("邮件服务器拒绝了收件地址，请检查163邮箱地址。", "recipient_rejected")
    if isinstance(error,(smtplib.SMTPSenderRefused,smtplib.SMTPDataError)):
        return MailError("邮件服务器拒绝了本次邮件（状态码"+str(error.smtp_code)+"）。", "smtp_rejected")
    if during_data:
        return MailError("投递途中连接中断，结果未确认。请先检查163收件箱，程序不会自动重发。", "unknown")
    return MailError("暂时未能连接QQ发信服务，请检查网络后重试。", "connection")


def open_smtp(config, password, factory=None):
    client = None
    try:
        client = (factory or smtplib.SMTP_SSL)(config["smtp_host"],config["smtp_port"],timeout=config["timeout_seconds"],context=ssl.create_default_context())
        client.ehlo()
        client.login(config["sender"],password)
        return client
    except (smtplib.SMTPException,OSError) as error:
        if client:
            client.close()
        raise smtp_error(error) from None


def close_smtp(client):
    try:
        client.quit()
    except (smtplib.SMTPException,OSError):
        client.close()


def check_auth(config, password=None, factory=None):
    client = open_smtp(config,password or read_password(config),factory)
    close_smtp(client)
    return {"ok":True,"message":"QQ发信账号验证成功，尚未发送邮件。"}


def send(edition, config=None, root=ROOT, password=None, factory=None):
    config = config or load_config(root)
    path = receipt_path(edition,config,root)
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (path.parent / ".send.lock").open("a") as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise MailError("另一封报纸正在发送，请稍后查看状态。", "busy") from None
        previous = receipt(edition,config,root)
        if previous["status"] == "accepted":
            return previous
        if previous["status"] in ("sending","unknown"):
            raise MailError("上次投递结果未确认，请先检查163收件箱，避免重复发送。", "unknown")
        message, manifest = prepare(edition,config,root)
        password = password or read_password(config)
        state = {**manifest,"status":"connecting","attempted_at":datetime.now(LOCAL).isoformat()}
        private_json(path,state)
        client = None
        during_data = False
        try:
            client = open_smtp(config,password,factory)
            state["status"] = "sending"
            private_json(path,state)
            during_data = True
            refused = client.send_message(message,from_addr=config["sender"],to_addrs=config["recipients"])
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
            state.update(status="accepted",accepted_at=datetime.now(LOCAL).isoformat(),message="QQ服务器已接受邮件，请查看163收件箱或垃圾邮件。")
            private_json(path,state)
        except MailError as error:
            state.update(status="failed",error_code=error.code,message=str(error))
            private_json(path,state)
            raise
        except (smtplib.SMTPException,OSError) as error:
            friendly = smtp_error(error,during_data)
            state.update(status="unknown" if friendly.code=="unknown" else "failed",error_code=friendly.code,message=str(friendly))
            private_json(path,state)
            raise friendly from None
        finally:
            if client:
                close_smtp(client)
        return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition",required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--send",action="store_true")
    group.add_argument("--check-auth",action="store_true")
    group.add_argument("--status",action="store_true")
    args = parser.parse_args()
    try:
        config = load_config()
        if args.send:
            result = send(args.edition,config)
        elif args.check_auth:
            result = check_auth(config)
        elif args.status:
            result = receipt(args.edition,config)
        else:
            _, manifest = prepare(args.edition,config)
            result = {**manifest,"status":"preview_only","messages_sent":0}
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except MailError as error:
        print(json.dumps({"ok":False,"code":error.code,"message":str(error)},ensure_ascii=False))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
