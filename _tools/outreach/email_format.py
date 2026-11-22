"""Build the outreach email (plain text + HTML) for one lead.

Usage:
  python3 email_format.py "<opening line>" "<demo url>" <Yes|No call button> <image path>

Prints JSON with body, htmlBody and the inline attachment reference for the
Gmail send_message tool. The image goes inline as cid:att0 and links to the demo.
No customer data lives in this file.
"""
import hashlib
import html
import json
import os
import sys

SIGNATURE = ["Todd DeLuise", "Lake Houston Web Co", "(979) 355-0557", "lakehoustonwebco.com"]
OPT_OUT = 'If you would rather not hear from me again, just reply "no thanks" and I won\'t follow up.'


def paragraph(call_button):
    has = ("a quote request form and a tap-to-call button" if call_button
           else "and a quote request form")
    return ("It has your services, a side-by-side look at where you stand online today, "
            f"{has}. I can add your real photos, prices and hours. If you like it, I can put it "
            "on your own domain for a one-time $500, with any changes you want. If not, no worries.")


def build(hook, url, call_button, image):
    para = paragraph(call_button)
    text = "\n".join([
        "Hi,", "",
        f"I'm Todd, and I build websites for small businesses. {hook}, so I made you a free website demo. "
        "I included a quick look at what you have now next to the demo I made you.", "",
        "Click the link for the full demo I made you:", url, "",
        para, "",
        "Check out my website to see more of my work: https://lakehoustonwebco.com", "",
        "Thanks,", *SIGNATURE, "",
        OPT_OUT,
    ])
    E = html.escape
    htm = (
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#222;max-width:600px">'
        f"<p>Hi,</p><p>I'm Todd, and I build websites for small businesses. {E(hook, quote=False)}, so I made you a free website demo. "
        "Here's a quick look at what you have now next to the demo I made you:</p>"
        f'<p><a href="{url}"><img src="cid:att0" width="600" alt="What you have now vs. the demo I made you" '
        'style="width:100%;max-width:600px;height:auto;border:0;display:block;border-radius:8px"></a></p>'
        f'<p><b>Click the link for the full demo I made you:</b><br><a href="{url}">{url}</a></p>'
        f"<p>{E(para, quote=False)}</p>"
        '<p>Check out my website to see more of my work: <a href="https://lakehoustonwebco.com">https://lakehoustonwebco.com</a></p>'
        f"<p>Thanks,<br>{'<br>'.join(SIGNATURE)}</p>"
        f'<p style="color:#777;font-size:13px">{E(OPT_OUT, quote=False)}</p></div>'
    )
    image = os.path.abspath(image)
    digest = hashlib.sha256(open(image, "rb").read()).hexdigest()
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return {
        "body": text,
        "htmlBody": htm,
        "attachments": [{"content": f"sha256:{digest}:{image}", "filename": f"{slug}-preview.jpg",
                         "mimeType": "image/jpeg", "inline": True}],
    }


if __name__ == "__main__":
    hook, url, call, image = sys.argv[1:5]
    print(json.dumps(build(hook, url, call.strip().lower() in ("yes", "y", "true", "1"), image),
                     ensure_ascii=False, indent=1))
