"""
Email Service cho AptisKey – Gửi email qua Resend API.
Nếu RESEND_API_KEY chưa cấu hình, in reset link ra console để developer test ngay.
"""
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_reset_email_html(reset_link: str, user_name: str) -> str:
    """Tạo nội dung email HTML Neumorphism-style đẹp."""
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Đặt lại mật khẩu – AptisKey</title>
</head>
<body style="margin:0;padding:0;background-color:#e0e5ec;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#e0e5ec;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
          style="background-color:#e0e5ec;border-radius:24px;
                 box-shadow:8px 8px 20px #a3b1c6,-8px -8px 20px #ffffff;
                 padding:40px 44px;max-width:560px;">

          <!-- Logo / Brand -->
          <tr>
            <td align="center" style="padding-bottom:28px;">
              <div style="display:inline-block;background:linear-gradient(135deg,#5b9bff,#6c63ff);
                          border-radius:16px;padding:12px 20px;
                          box-shadow:4px 4px 12px #a3b1c6,-4px -4px 8px #ffffff;">
                <span style="font-size:22px;font-weight:900;color:#fff;letter-spacing:-1px;">AK</span>
              </div>
              <div style="font-size:22px;font-weight:800;
                          background:linear-gradient(135deg,#4f8ef7,#6c63ff);
                          -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                          margin-top:8px;">AptisKey</div>
            </td>
          </tr>

          <!-- Heading -->
          <tr>
            <td align="center" style="padding-bottom:12px;">
              <h1 style="margin:0;font-size:26px;font-weight:800;color:#2d3748;">
                🔑 Đặt lại mật khẩu
              </h1>
            </td>
          </tr>

          <!-- Body text -->
          <tr>
            <td style="padding:0 0 28px 0;color:#4a5568;font-size:15px;line-height:1.7;text-align:center;">
              Xin chào <strong>{user_name}</strong>!<br/>
              Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản AptisKey của bạn.
              Nhấn vào nút bên dưới để tiếp tục. Link sẽ hết hạn sau <strong>15 phút</strong>.
            </td>
          </tr>

          <!-- CTA Button -->
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <a href="{reset_link}" target="_blank"
                style="display:inline-block;padding:15px 40px;
                       background:linear-gradient(145deg,#5b9bff,#4080ed);
                       color:#ffffff;text-decoration:none;border-radius:9999px;
                       font-size:16px;font-weight:800;letter-spacing:0.03em;
                       box-shadow:5px 5px 12px #a3b1c6,-3px -3px 8px #ffffff,
                                  0 4px 20px rgba(79,142,247,0.35);">
                Đặt lại mật khẩu ngay →
              </a>
            </td>
          </tr>

          <!-- Fallback link -->
          <tr>
            <td style="padding:0 0 24px 0;">
              <div style="background-color:#e0e5ec;border-radius:12px;padding:16px;
                          box-shadow:inset 3px 3px 8px #a3b1c6,inset -3px -3px 8px #ffffff;">
                <p style="margin:0 0 6px 0;font-size:12px;color:#718096;font-weight:700;
                           text-transform:uppercase;letter-spacing:0.08em;">
                  Nếu nút không hoạt động, copy link này:
                </p>
                <p style="margin:0;font-size:12px;color:#4f8ef7;word-break:break-all;">
                  {reset_link}
                </p>
              </div>
            </td>
          </tr>

          <!-- Warning -->
          <tr>
            <td style="padding:0 0 16px 0;font-size:13px;color:#718096;text-align:center;line-height:1.6;">
              Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.<br/>
              Tài khoản của bạn vẫn an toàn.
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding-top:20px;border-top:1px solid rgba(163,177,198,0.4);
                       text-align:center;font-size:12px;color:#a0aec0;">
              © 2026 AptisKey · Hệ thống ôn luyện Aptis thông minh
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


async def send_reset_password_email(to_email: str, reset_link: str, user_name: str) -> bool:
    """
    Gửi email đặt lại mật khẩu.
    - Nếu RESEND_API_KEY được cấu hình: gửi email thật qua Resend API.
    - Nếu chưa cấu hình: in reset_link ra console log để test.
    Trả về True nếu thành công (hoặc mode dev), False nếu lỗi khi gửi thật.
    """
    reset_key = settings.RESEND_API_KEY

    # -- DEV MODE: chua cau hinh key --------------------------------------------
    if not reset_key or reset_key.startswith("THAY_THE"):
        logger.warning("[AptisKey] RESEND_API_KEY chua cau hinh - DEV LOG MODE")
        logger.warning("[AptisKey] To: %s", to_email)
        logger.warning("[AptisKey] Reset Link: %s", reset_link)
        try:
            print("\n" + "=" * 70, flush=True)
            print(f"[DEV] Reset Password Email to: {to_email}", flush=True)
            print(f"[DEV] Reset Link (expires 15 min): {reset_link}", flush=True)
            print("=" * 70 + "\n", flush=True)
        except UnicodeEncodeError:
            # Windows cp1252 fallback
            import sys
            out = sys.stdout
            out.buffer.write(("\n" + "=" * 70 + "\n").encode('utf-8'))
            out.buffer.write(f"[DEV] Reset Password Email to: {to_email}\n".encode('utf-8'))
            out.buffer.write(f"[DEV] Reset Link (15min): {reset_link}\n".encode('utf-8'))
            out.buffer.write(("=" * 70 + "\n\n").encode('utf-8'))
            out.buffer.flush()
        return True

    # ── PRODUCTION MODE: gửi email thật qua Resend API ─────────────────────────
    try:
        import httpx
        html_content = _build_reset_email_html(reset_link, user_name)
        payload = {
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [to_email],
            "subject": "🔑 Đặt lại mật khẩu AptisKey của bạn",
            "html": html_content,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={"Authorization": f"Bearer {reset_key}"},
                timeout=10.0,
            )
        if resp.status_code in (200, 201):
            logger.info(f"✅ Đã gửi reset email tới {to_email} (id={resp.json().get('id')})")
            return True
        else:
            logger.error(f"❌ Resend API lỗi {resp.status_code}: {resp.text}")
            return False
    except Exception as exc:
        logger.error(f"❌ Lỗi khi gửi email: {exc}")
        return False
