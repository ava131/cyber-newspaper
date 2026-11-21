import argparse
import hmac
import json
import secrets
import threading
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from mail_delivery import ROOT, MailError, check_auth, credential_present, load_config, prepare, private_json, receipt, send, store_password, validate_password

STYLE = """
*{box-sizing:border-box}body{margin:0;background:#e7e1d3;color:#27251f;font-family:'PingFang SC',Arial,sans-serif;line-height:1.75}.wrap{max-width:880px;margin:36px auto;padding:0 20px 60px}.masthead{border-bottom:4px double #27251f;padding-bottom:18px;margin-bottom:24px;display:flex;justify-content:space-between;gap:15px;align-items:end}.masthead h1{font:38px 'Songti SC',serif;letter-spacing:.08em;margin:0}.masthead span{font-size:12px;color:#6e6657}.card{background:#f6f1e4;border:1px solid #c9bda5;padding:24px 28px;margin-bottom:18px}.card h2{font:24px 'Songti SC',serif;margin:0 0 15px}.card p{margin:8px 0}.meta{display:grid;grid-template-columns:80px 1fr;gap:7px 15px;font-size:14px}.meta span{color:#77705f}.steps{padding-left:24px;margin:0}.steps li{margin:8px 0}.note{color:#766d5b;font-size:13px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0 0}button,.button{padding:11px 18px;border:1px solid #37342b;background:#37342b;color:#f7f1e4;font:14px inherit;cursor:pointer;text-decoration:none;display:inline-block}button:disabled{opacity:.4;cursor:default}.secondary{background:transparent;color:#37342b}label{display:block;font-size:14px;margin:16px 0 7px}input{width:100%;font:18px ui-monospace,monospace;letter-spacing:.12em;padding:12px 14px;background:#fffdf7;border:1px solid #b1a48b;border-radius:0}input:focus{outline:2px solid #9d783e;outline-offset:2px}.status{padding:14px 18px;background:#e8e0ca;border-left:3px solid #8b6a38;font-size:14px;min-height:54px;margin-top:18px;white-space:pre-line}.status.error{border-left-color:#a43c2e;background:#f1ded5}.status.success{border-left-color:#3b7055;background:#deeadf}iframe{width:100%;height:680px;border:1px solid #d4c9b5;background:#fff;margin-top:18px}.tag{font-size:11px;color:#8b312b;letter-spacing:.12em}.consent{font-size:13px;color:#6f6554;line-height:1.9}.footer{font-size:12px;color:#746b5b;text-align:center;padding:12px}@media(max-width:600px){.wrap{padding:0 12px 35px;margin-top:20px}.masthead{display:block}.masthead h1{font-size:32px}.card{padding:20px}.meta{grid-template-columns:65px 1fr;font-size:12px;gap:8px}.meta b{overflow-wrap:anywhere}.card h2{font-size:23px}iframe{height:600px}.actions button,.actions a{flex:1;text-align:center;padding:12px}.masthead span{display:block;margin-top:10px}}
"""

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>赛博日报 · QQ邮箱设置</title><link rel="stylesheet" href="/style.css"></head><body><main class="wrap"><header class="masthead"><h1>赛博日报 · 邮箱设置</h1><span>一次配置，以后由程序投递</span></header>
<section class="card"><div class="tag">本次投递</div><h2>从QQ邮箱，送到你的163邮箱</h2><div class="meta"><span>发件人</span><b id="sender"></b><span>收件人</span><b id="recipient"></b><span>邮件主题</span><b id="subject"></b><span>完整报纸</span><b id="attachment"></b></div><p class="note">邮件正文是天气与各栏导读，完整六版报纸放在HTML附件里。</p></section>
<section class="card"><h2>1. 在QQ邮箱生成授权码</h2><ol class="steps"><li>打开QQ邮箱，登录发件账号。</li><li>进入「设置 → 账号与安全 → 安全设置」，找到「IMAP/SMTP服务」。旧版界面可能在「设置 → 账户」中。</li><li>开启服务、生成授权码，并按QQ提示完成扫码或短信验证。</li></ol><div class="actions"><a class="button secondary" href="https://mail.qq.com/" target="_blank" rel="noopener noreferrer">打开QQ邮箱 ↗</a></div></section>
<section class="card"><h2>2. 把授权码保存在这台Mac</h2><p class="note">授权码是QQ给发信程序的专用凭证，不是QQ登录密码。输入后保存到Mac钥匙串，不写入项目文件。</p><form id="credential-form"><label for="authorization-code">QQ邮箱客户端授权码</label><input id="authorization-code" type="password" autocomplete="new-password" spellcheck="false" maxlength="80" placeholder="粘贴授权码"><div class="actions"><button id="verify" type="submit">保存并验证</button></div></form><p class="note" id="saved-note"></p></section>
<section class="card"><h2>3. 看一眼，然后发送</h2><p class="consent">点击下方发送按钮，会从上面的QQ邮箱向上述163地址发送这一天的报纸。验证账号不会发送邮件。同一期成功提交后，程序会拦住重复发送。</p><iframe src="/preview" title="邮件正文预览" sandbox="allow-same-origin"></iframe><div class="actions"><button id="send" disabled>发送这份报纸</button><a class="button secondary" href="/download" download>下载邮件预览</a></div><div id="status" class="status" role="status">等待配置QQ邮箱授权码。</div></section><footer class="footer">此设置页只在这台电脑的本地地址运行。</footer></main><script src="/app.js"></script></body></html>"""

SCRIPT = """
const setupToken=__TOKEN__;
let busy=false;
let currentState=null;
const statusBox=document.querySelector('#status');
function show(message,kind=''){statusBox.textContent=message;statusBox.className='status '+kind}
function display(state){
  currentState=state;
  document.querySelector('#sender').textContent=state.manifest.sender;
  document.querySelector('#recipient').textContent=state.manifest.recipients.join(', ');
  document.querySelector('#subject').textContent=state.manifest.subject;
  document.querySelector('#attachment').textContent=state.manifest.attachment+' · '+(state.manifest.attachment_bytes/1024/1024).toFixed(2)+' MB';
  document.querySelector('#saved-note').textContent=state.credential_saved?'授权码已存于本机钥匙串。'+(state.verified?'QQ账号验证成功。':'可留空输入框，点击上方按钮验证已保存账号。'):'';
  document.querySelector('#verify').disabled=busy;
  const terminal=['accepted','sending','unknown'].includes(state.receipt.status);
  document.querySelector('#send').disabled=busy||!state.verified||terminal;
  if(state.receipt.status==='accepted')show('QQ服务器已接受这封报纸。请查看163收件箱或垃圾邮件。','success');
  else if(['sending','unknown'].includes(state.receipt.status))show('上一轮投递结果尚未确认，请先检查163收件箱，避免重复发送。','error');
}
async function refresh(){const response=await fetch('/api/status',{cache:'no-store'});if(response.ok)display(await response.json())}
async function action(path,payload){
  busy=true;if(currentState)display(currentState);
  try{
    const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Setup-Token':setupToken},body:JSON.stringify(payload)});
    const result=await response.json();
    if(result.state)display(result.state);
    show(result.message,result.ok?'success':'error');
  }catch{show('连接暂时中断。请刷新状态；如刚才正在发送，先查收件箱再重试。','error')}
  finally{busy=false;if(currentState)display(currentState)}
}
document.querySelector('#credential-form').addEventListener('submit',async event=>{
  event.preventDefault();
  const input=document.querySelector('#authorization-code');
  const code=input.value;input.value='';
  show('正在验证QQ账号并保存到本机钥匙串；如Mac弹出钥匙串提示，请按提示允许。');
  await action('/api/credential',{authorization_code:code});
});
document.querySelector('#send').addEventListener('click',async()=>{
  show('正在发送报纸，请稍候。');
  await action('/api/send',{edition:currentState.manifest.edition,recipients:currentState.manifest.recipients});
});
refresh().catch(()=>show('无法连接本机配置服务，请重新打开配置页。','error'));
setInterval(()=>{if(!busy)refresh().catch(()=>{})},4000);
"""


class Setup:
    def __init__(self,edition):
        self.edition = edition
        self.config = load_config()
        _, self.manifest = prepare(edition,self.config)
        self.token = secrets.token_urlsafe(32)
        self.origin = None
        self.host = None
        self.saved = credential_present(self.config)
        self.verified = False
        self.lock = threading.Lock()

    def state(self):
        return {"manifest":self.manifest,"credential_saved":self.saved,"verified":self.verified,"receipt":receipt(self.edition,self.config)}


def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass

        def answer(self,status,data,content_type="application/json; charset=utf-8",cookie=False,attachment=False):
            if isinstance(data,(dict,list)):
                data = json.dumps(data,ensure_ascii=False).encode()
            elif isinstance(data,str):
                data = data.encode()
            self.send_response(status)
            self.send_header("Content-Type",content_type)
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Referrer-Policy","no-referrer")
            ancestors = "'self'" if urlparse(self.path).path=="/preview" else "'none'"
            self.send_header("Content-Security-Policy",f"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors {ancestors}; base-uri 'none'; form-action 'self'")
            if cookie:
                self.send_header("Set-Cookie",f"cyber_mail_setup={app.token}; HttpOnly; SameSite=Strict; Path=/")
            if attachment:
                self.send_header("Content-Disposition",f'attachment; filename="cyber-daily-{app.edition}.eml"')
            self.end_headers()
            self.wfile.write(data)

        def valid_host(self):
            return self.headers.get("Host") == app.host

        def valid_action(self):
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get("Cookie",""))
                token = cookie.get("cyber_mail_setup")
                return self.valid_host() and self.headers.get("Origin")==app.origin and self.headers.get("Content-Type","").split(";",1)[0]=="application/json" and token and hmac.compare_digest(token.value,app.token) and hmac.compare_digest(self.headers.get("X-Setup-Token",""),app.token)
            except Exception:
                return False

        def do_GET(self):
            if not self.valid_host():
                return self.answer(403,{"ok":False})
            path = urlparse(self.path).path
            if path == "/":
                self.answer(200,PAGE,"text/html; charset=utf-8",cookie=True)
            elif path == "/app.js":
                self.answer(200,SCRIPT.replace("__TOKEN__",json.dumps(app.token)),"application/javascript; charset=utf-8")
            elif path == "/style.css":
                self.answer(200,STYLE,"text/css; charset=utf-8")
            elif path == "/preview":
                self.answer(200,(ROOT/"data/editions"/app.edition/"mail/preview.html").read_bytes(),"text/html; charset=utf-8")
            elif path == "/download":
                self.answer(200,(ROOT/"data/editions"/app.edition/"mail/message.eml").read_bytes(),"message/rfc822",attachment=True)
            elif path == "/api/status":
                self.answer(200,app.state())
            else:
                self.answer(404,{"ok":False})

        def do_POST(self):
            if not self.valid_action():
                return self.answer(403,{"ok":False,"message":"本机会话校验未通过，请从配置页重新操作。"})
            path = urlparse(self.path).path
            if path not in ("/api/credential","/api/send"):
                return self.answer(404,{"ok":False})
            try:
                length = int(self.headers.get("Content-Length","0"))
                if not 0 < length <= 4096:
                    return self.answer(400,{"ok":False,"message":"请求内容格式不正确。"})
                payload = json.loads(self.rfile.read(length))
            except (ValueError,UnicodeDecodeError):
                return self.answer(400,{"ok":False,"message":"请求内容格式不正确。"})
            if not app.lock.acquire(blocking=False):
                return self.answer(409,{"ok":False,"message":"上一项操作仍在进行，请稍候。"})
            try:
                if path == "/api/credential":
                    code = payload.get("authorization_code","")
                    if not isinstance(code,str):
                        raise MailError("授权码格式不正确。", "credential_format")
                    code = validate_password(code) if code else ""
                    check_auth(app.config,code or None)
                    if code:
                        store_password(app.config,code)
                    app.saved = True
                    app.verified = True
                    message = "QQ账号验证成功，授权码已保存在本机钥匙串。你可以查看预览并发送报纸。"
                    print(json.dumps({"event":"credential_verified","edition":app.edition},ensure_ascii=False),flush=True)
                else:
                    if not app.verified:
                        raise MailError("请先验证QQ发信账号。", "verification_required")
                    if payload.get("edition") != app.edition or payload.get("recipients") != app.config["recipients"]:
                        raise MailError("发送日期或收件地址与预览不一致。", "preview_mismatch")
                    result = send(app.edition,app.config)
                    message = result["message"]
                    print(json.dumps({"event":"mail_submitted","edition":app.edition,"status":result["status"]},ensure_ascii=False),flush=True)
                self.answer(200,{"ok":True,"message":message,"state":app.state()})
            except MailError as error:
                self.answer(400,{"ok":False,"code":error.code,"message":str(error),"state":app.state()})
            except Exception:
                self.answer(500,{"ok":False,"message":"本机配置未完成，请检查系统提示后重试。","state":app.state()})
            finally:
                app.lock.release()

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition",required=True)
    parser.add_argument("--port",type=int,default=0)
    args = parser.parse_args()
    app = Setup(args.edition)
    server = ThreadingHTTPServer(("127.0.0.1",args.port),handler_for(app))
    app.host = "127.0.0.1:"+str(server.server_address[1])
    app.origin = "http://"+app.host
    private_json(ROOT/".local/mail/setup-session.json",{"url":app.origin,"edition":app.edition,"credential_saved":app.saved,"messages_sent":0})
    print(json.dumps({"setup_url":app.origin,"edition":app.edition,"credential_saved":app.saved,"messages_sent":0},ensure_ascii=False),flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
