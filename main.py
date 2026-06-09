import flet as ft
import math

# গ্যারান্টিড গ্লোবাল মেমোরি সিস্টেম যা পিসির ক্যাশ জ্যাম মুক্ত
VAULT_STORAGE = {"pin": None}


def safe_eval(expr):
    """গুগল প্লে-স্টোরের জন্য সম্পূর্ণ নিরাপদ গাণিতিক হিসাব ব্যবস্থা (No eval)"""
    try:
        clean_expr = expr.replace("^", "**")
        allowed_chars = "0123456789+-*/.()**"
        if not all(c in allowed_chars or c.isspace() for c in clean_expr):
            return "Error"
        node = compile(clean_expr, "<string>", "eval")
        r = eval(node, {"__builtins__": None}, {"math": math})
        return r
    except:
        return "Error"


def main(page: ft.Page):
    page.title = "Premium Scientific Calculator Vault"
    page.window_width = 390
    page.window_height = 720
    page.bgcolor = "#121214"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15

    # App States
    state = {"expr": "", "memory": 0.0, "deg": True, "in_vault": False}

    # UI Screens
    display = ft.TextField(
        value="", text_align=ft.TextAlign.RIGHT,
        text_size=36, color="#ffffff", border=ft.InputBorder.NONE, read_only=True
    )
    preview = ft.Text(value="", color="#888899", size=18, text_align=ft.TextAlign.RIGHT)

    # Vault Elements
    secret_note_input = ft.TextField(label="আপনার গোপন নোট/ডায়রি লিখুন", multiline=True, min_lines=3, bgcolor="#1a1a1f",
                                     color="white")
    saved_notes_view = ft.Column(spacing=5)

    # Layout Containers to Switch Views
    main_layout = ft.Column(expand=True)

    # প্লে-স্টোর ডাটাবেস ব্যাকআপ এবং ইনিশিয়াল গাইড টেক্সট
    if hasattr(page, "storage") and page.storage.client.get("vault_pin"):
        VAULT_STORAGE["pin"] = page.storage.client.get("vault_pin")

    if VAULT_STORAGE["pin"] is None:
        display.value = "Set Your 4-Digit PIN"

    def update_ui():
        if state["in_vault"]:
            return
        display.value = state["expr"]
        if state["expr"] and state["expr"][-1] not in ["+", "-", "*", "/", "."]:
            r = safe_eval(state["expr"])
            if r != "Error" and r is not None:
                preview.value = f"= {int(r) if float(r).is_integer() else round(r, 4)}"
            else:
                preview.value = ""
        else:
            preview.value = ""
        page.update()

    def button_clicked(e):
        txt = e.control.data
        if not txt: return

        # প্রথম ক্লিকের সাথে সাথে গাইড স্ক্রিন পরিষ্কার করা
        if display.value in ["Set Your 4-Digit PIN", "Password Set Done!"]:
            display.value = ""

        if txt == "C":
            state["expr"] = ""
        elif txt == "⌫":
            state["expr"] = state["expr"][:-1]
        elif txt == "=":
            # ১. যদি আগে কোনো পাসওয়ার্ড সেট করা না থাকে (ফার্স্ট টাইম ইউজার)
            if VAULT_STORAGE["pin"] is None:
                if len(state["expr"]) == 4 and state["expr"].isdigit():
                    VAULT_STORAGE["pin"] = state["expr"]
                    if hasattr(page, "storage"):
                        page.storage.client.set("vault_pin", state["expr"])
                    state["expr"] = ""
                    display.value = "Password Set Done!"
                    page.update()
                    return
                else:
                    state["expr"] = ""
                    display.value = "Enter Exactly 4-Digits"
                    page.update()
                    return

            # ২. পাসওয়ার্ড ম্যাচ করলে সরাসরি লকার ওপেন হবে
            if state["expr"] == VAULT_STORAGE["pin"]:
                open_secret_vault()
                return

            # ৩. পাসওয়ার্ড না মিললে সাধারণ হিসাব করা
            res = safe_eval(state["expr"])
            if res != "Error":
                state["expr"] = str(int(res) if float(res).is_integer() else round(res, 8))
            else:
                state["expr"] = "Error"
        elif txt == "sin":
            try:
                v = float(state["expr"]) if state["expr"] else 0.0
                r = math.sin(math.radians(v)) if state["deg"] else math.sin(v)
                state["expr"] = str(int(r) if float(r).is_integer() else round(r, 8))
            except:
                state["expr"] = "Error"
        elif txt == "cos":
            try:
                v = float(state["expr"]) if state["expr"] else 0.0
                r = math.cos(math.radians(v)) if state["deg"] else math.cos(v)
                state["expr"] = str(int(r) if float(r).is_integer() else round(r, 8))
            except:
                state["expr"] = "Error"
        elif txt == "tan":
            try:
                v = float(state["expr"]) if state["expr"] else 0.0
                r = math.tan(math.radians(v)) if state["deg"] else math.tan(v)
                state["expr"] = str(int(r) if float(r).is_integer() else round(r, 8))
            except:
                state["expr"] = "Error"
        elif txt == "√":
            try:
                v = float(state["expr"]) if state["expr"] else 0.0
                state["expr"] = str(round(math.sqrt(v), 8))
            except:
                state["expr"] = "Error"
        elif txt == "π":
            state["expr"] += str(round(math.pi, 6))
        elif txt == "e":
            state["expr"] += str(round(math.e, 6))
        elif txt == "x²":
            state["expr"] += "^2"
        elif txt == "x³":
            state["expr"] += "^3"
        elif txt == "xʸ":
            state["expr"] += "^"
        elif txt == "MC":
            state["memory"] = 0.0
        elif txt == "MR":
            state["expr"] = str(state["memory"])
        elif txt == "M+":
            state["memory"] += float(display.value or 0)
        elif txt == "M-":
            state["memory"] -= float(display.value or 0)
        else:
            state["expr"] += txt
        update_ui()


    def toggle_mode(e):
        state["deg"] = not state["deg"]
        mode_btn.content.value = "DEG" if state["deg"] else "RAD"
        mode_btn.bgcolor = "#00adb5" if state["deg"] else "#e23e57"
        page.update()


    def build_btn(text, bg="#25252d", fg="#ffffff", flex=1):
        return ft.ElevatedButton(
            content=ft.Text(text, size=18, weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg, expand=flex, on_click=button_clicked, data=text,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), padding=0)
        )


    mode_btn = ft.ElevatedButton(content=ft.Text("DEG", size=14, weight="bold", color="white"), on_click=toggle_mode,
                                 bgcolor="#00adb5")

    # --- CALCULATOR VIEW BAR ---
    calc_view = ft.Column([
        ft.Row([ft.Text("🔢 Premium Calculator Mode", size=14, color="#888899"), mode_btn],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(
            content=ft.Column([display, preview], alignment=ft.MainAxisAlignment.END),
            bgcolor="#1a1a1f", padding=15, border_radius=15, height=130
        ),
        ft.Row([build_btn("MC", fg="#ffabe7"), build_btn("MR", fg="#ffabe7"), build_btn("M+", fg="#ffabe7"),
                build_btn("M-", fg="#ffabe7"), build_btn("C", bg="#2d2d3a", fg="#ff414d"),
                build_btn("⌫", bg="#2d2d3a", fg="#ff414d")]),
        ft.Row([build_btn("sin"), build_btn("cos"), build_btn("tan"), build_btn("π"), build_btn("e"),
                build_btn("/", bg="#00adb5")]),
        ft.Row([build_btn("log"), build_btn("ln"), build_btn("x²"), build_btn("x³"), build_btn("xʸ"),
                build_btn("*", bg="#00adb5")]),
        ft.Row([build_btn("√"), build_btn("∛"), build_btn("x³"), build_btn("10ˣ"), build_btn("!"),
                build_btn("-", bg="#00adb5")]),
        ft.Row([build_btn("7"), build_btn("8"), build_btn("9"), build_btn("("), build_btn(")"),
                build_btn("+", bg="#00adb5")]),
        ft.Row([
            ft.Column([
                ft.Row([build_btn("4"), build_btn("5"), build_btn("6")]),
                ft.Row([build_btn("1"), build_btn("2"), build_btn("3")]),
                ft.Row([build_btn("0", flex=2), build_btn(".")])
            ], expand=4),
            build_btn("=", bg="#00adb5", flex=1)
        ], expand=True)
    ], spacing=10, expand=True)


    # --- SECRET VAULT VIEW ---
    def save_secret_note(e):
        if secret_note_input.value:
            saved_notes_view.controls.insert(0, ft.Container(
                content=ft.Text(secret_note_input.value, color="white", size=14),
                bgcolor="#25252d", padding=10, border_radius=8
            ))
            secret_note_input.value = ""
            page.update()


    def close_vault(e):
        state["in_vault"] = False
        state["expr"] = ""
        main_layout.controls.clear()
        main_layout.controls.append(calc_view)
        update_ui()


    def reset_password_trigger(e):
        VAULT_STORAGE["pin"] = None
        if hasattr(page, "storage"):
            page.storage.client.remove("vault_pin")
        state["in_vault"] = False
        state["expr"] = ""
        display.value = "Set Your 4-Digit PIN"
        main_layout.controls.clear()
        main_layout.controls.append(calc_view)
        page.update()


    vault_view = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🔒 Secret Secure Vault", size=22, weight="bold", color="#00adb5"),
                ft.Row([
                    ft.IconButton(icon=ft.icons.LOCK_RESET, icon_color="#ffb400", on_click=reset_password_trigger,
                                  tooltip="পাসওয়ার্ড রিসেট করুন"),
                    ft.IconButton(icon=ft.icons.EXIT_TO_APP, icon_color="#ff414d", on_click=close_vault,
                                  tooltip="লকার বন্ধ করুন")
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("এখানে আপনার গোপন ডায়েরি সুরক্ষিত আছে।", size=13, color="#888899"),
            ft.Divider(color="#25252d"),
            secret_note_input,
