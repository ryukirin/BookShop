"""静态源码冻结的活动路由登记；业务处理按后续批次接入。"""
from flask import abort, redirect, request

PREFIX = "/BookShop"

OPERATIONS = {
    "login.action": {
        "addusers": ("inputUname", "inputPassword", "checkPassword"),
        "checkUsers": ("inputName", "inputPassword"),
    },
    "jsp/my.action": {
        "initMypage": (),
        "queryMyorder": (),
        "updatePwd": ("oldpwd", "newpwd", "anewpwd"),
    },
    "jsp/book.action": {
        "queryAllbook": (),
        "queryByname": ("bname",),
        "queryBytag": ("tname",),
        "bookDetail": ("bid",),
        "buybook": ("bid",),
    },
    "jsp/admin.action": {
        "queryAllcustomers": (),
        "queryCustomers": ("uname",),
        "deleteCustomers": ("uid",),
        "queryAllbooks": (),
        "queryBooks": ("bname",),
        "addBooks": ("bname", "publishers", "stock", "price", "tname", "cont"),
        "addBooksimg": (),
        "showBooks": ("bid",),
        "editBooks": ("bid", "publishers", "stock", "price"),
        "deleteBooks": ("bid",),
        "showAllmoney": (),
    },
}
WRITE_OPERATIONS = {
    "login.action": frozenset(("addusers", "checkUsers")),
    "jsp/my.action": frozenset(("updatePwd",)),
    "jsp/book.action": frozenset(("buybook",)),
    "jsp/admin.action": frozenset(("deleteCustomers", "addBooks", "addBooksimg",
                                   "editBooks", "deleteBooks")),
}
ACTIVE_PAGES = (
    "index.jsp", "login.jsp", "register.jsp",
    "jsp/buy.jsp", "jsp/bookdetails.jsp", "jsp/my.jsp", "jsp/myorder.jsp",
    "jsp/changepwd.jsp", "jsp/admin.jsp", "jsp/bookadmin.jsp",
    "jsp/add.jsp", "jsp/addnext.jsp", "jsp/editbook.jsp",
    "jsp/oderadmin.jsp", "jsp/showpic.jsp",
)


def register_foundation_routes(app):
    @app.get(PREFIX + "/health")
    def health():
        return "ok", 200

    @app.get(PREFIX + "/")
    def home():
        return redirect(PREFIX + "/index.jsp")

    for page in ACTIVE_PAGES:
        app.add_url_rule(PREFIX + "/" + page,
                         "page_" + page.replace("/", "_").replace(".", "_"),
                         lambda: ("功能尚未迁移", 501), methods=["GET"])

    for path, operations in OPERATIONS.items():
        def route(path=path, operations=operations):
            operation = request.args.get("opttype")
            if operation not in operations:
                abort(400)
            if request.method == "GET" and operation in WRITE_OPERATIONS.get(path, ()):
                abort(405)
            for parameter in operations[operation]:
                if parameter not in request.values:
                    abort(400)
            return "功能尚未迁移", 501
        app.add_url_rule(PREFIX + "/" + path,
                         "action_" + path.replace("/", "_").replace(".", "_"),
                         route, methods=["GET", "POST"])
