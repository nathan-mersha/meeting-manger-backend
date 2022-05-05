import re

exception_routes = [
        "server",
        "server/user/signup",
        "server/user/login",
        "server/user/forgot_password",
        "server/user/reset_password",
        "server/user/verify/email",
        "server/user/verify/phone_number",
        "server/user/request/verification/email",
        "server/user/request/verification/phone_number",
        "server/meeting/confirm_meeting/*",
        "docs",
        "openapi.json",
        "favicon.ico"
    ]

r1 = "/server/meeting/confirm_meeting/1/2/3"
for exception_route in exception_routes:
    matches = re.findall(exception_route, r1)
    print(f"{exception_route} passes {len(matches) > 0}")