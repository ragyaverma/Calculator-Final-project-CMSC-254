import sys
if sys.platform == "darwin":
    try:
        import multiprocessing
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass

# Imports for GUI and math operations 
import tkinter as tk
from tkinter import font, messagebox
import math

#  Color constants used for UI styling 
BG = "#35536B"
PANEL = "#f6f4f4"
BTN_GREY = "#9b9b9b"
BTN_WHITE = "#ffffff"
BTN_OP = "#000000"
BTN_CLEAR = "#d9534f"
ACCENT = "#2b8cff"
TEXT_DARK = "#0d0d0d"

# Font settings 
FONT_FAMILY = "Helvetica"
DISPLAY_FONT = (FONT_FAMILY, 28, "bold")
BTN_FONT = (FONT_FAMILY, 18)
SM_BTN_FONT = (FONT_FAMILY, 14)
#       CALCULATOR LOGIC
class Calculator:
    def __init__(self):
        # Reset variables when calculator starts
        self.reset_all()

    def reset_all(self):
        # Main state variables
        self.current = "0"       # What the display shows
        self.stored = None       # Stored number for operations
        self.operator = None     # Current chosen operator
        self.last_was_equal = False
        self.on = True           # Calculator power state

    def input_digit(self, ch):
        # Handles number or decimal input
        if not self.on:
            return
        if self.last_was_equal:
            # Start fresh after pressing '='
            self.current = "0"
            self.operator = None
            self.stored = None
            self.last_was_equal = False

        if ch == ".":
            # Prevent multiple decimals
            if "." not in self.current:
                self.current += "."
            return

        # Replace starting zero or append digit
        if self.current == "0":
            self.current = ch
        else:
            self.current += ch

    def toggle_sign(self):
        # Change positive to negative or vice-versa
        if not self.on:
            return
        if self.current.startswith("-"):
            self.current = self.current[1:]
        else:
            if self.current != "0":
                self.current = "-" + self.current

    def percent(self):
        # Convert current number to percentage (divide by 100)
        if not self.on:
            return
        try:
            val = float(self.current)
            val /= 100.0
            self.current = format_number(val)
        except:
            self.current = "Error"

    def clear_entry(self):
        # Clear only current input
        if not self.on:
            return
        self.current = "0"

    def backspace(self):
        # Delete last character
        if not self.on:
            return
        if self.last_was_equal:
            self.current = "0"
            self.last_was_equal = False
            return
        # If number becomes empty reset to 0
        if len(self.current) <= 1 or (len(self.current) == 2 and self.current.startswith("-")):
            self.current = "0"
        else:
            self.current = self.current[:-1]

    def choose_operator(self, op):
        # When user selects +, -, *, /
        if not self.on:
            return
        try:
            if self.stored is None:
                # First operator press stores the current number
                self.stored = float(self.current)
            else:
                # If an operation is pending, calculate it first
                self._compute_pending()
            self.operator = op
            self.current = "0"
            self.last_was_equal = False
        except Exception:
            self.current = "Error"

    def apply_sqrt(self):
        # Square root function
        if not self.on:
            return
        try:
            val = float(self.current)
            if val < 0:
                self.current = "Error: √ of negative"
            else:
                result = math.sqrt(val)
                self.current = format_number(result)
                self.last_was_equal = True
        except Exception:
            self.current = "Error"

    def press_equal(self):
        # Perform final computation when '=' is pressed
        if not self.on:
            return
        if self.operator is None:
            self.last_was_equal = True
            return
        try:
            self._compute_pending()
            self.operator = None
            self.last_was_equal = True
            self.stored = None
        except ZeroDivisionError:
            self.current = "Error: Division by 0"
        except ValueError:
            self.current = "Error"
        except OverflowError:
            self.current = "Overflow"
        except Exception:
            self.current = "Error"

    def _compute_pending(self):
        # Internal function that executes +, -, *, /, ^
        if self.operator is None or self.stored is None:
            return
        a = self.stored
        b = float(self.current)

        # Perform the chosen operation
        if self.operator == "+":
            res = a + b
        elif self.operator == "-":
            res = a - b
        elif self.operator == "*":
            res = a * b
        elif self.operator == "/":
            if b == 0:
                raise ZeroDivisionError
            res = a / b
        elif self.operator == "^":
            # Handle special exponent cases
            if a == 0 and b == 0:
                self.current = "Undefined (0^0)"
                self.stored = None
                self.operator = None
                raise ValueError("Undefined")
            if a < 0 and not b.is_integer():
                raise ValueError("Complex result")
            res = a ** b
        else:
            raise ValueError("Unknown operator")

        # Store result and update display
        self.current = format_number(res)
        self.stored = res

    def toggle_on_off(self):
        # Turns calculator on or off
        self.on = not self.on
        if not self.on:
            # Clear everything when turning off
            self.current = ""
            self.stored = None
            self.operator = None
            self.last_was_equal = False
        else:
            # Reset when turning back on
            self.reset_all()
#     NUMBER FORMATTING
def format_number(val):
    # Formats numbers to avoid long decimals and scientific issues
    try:
        if math.isinf(val) or math.isnan(val):
            return "Error"
        if abs(val) >= 1e10 or (abs(val) > 0 and abs(val) < 1e-8):
            return "{:.8e}".format(val)  # Use scientific notation
        if float(int(val)) == val:
            return str(int(val))         # Remove decimal if whole number
        s = "{:.10g}".format(val)
        return s
    except Exception:
        return "Error"


#    CALCULATOR GUI (Tk)
class CalculatorUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window basic settings
        self.title("Smart Calculator")
        self.configure(bg="#efefef")
        self.geometry("420x740")
        self.resizable(False, False)

        self.calc = Calculator()

        # Build UI parts
        self._build_fonts()
        self._build_ui()
        self._bind_keys()
        self._update_display()

    def _build_fonts(self):
        # Define fonts used in UI
        self.font_display = font.Font(family=FONT_FAMILY, size=28, weight="bold")
        self.font_btn = font.Font(family=FONT_FAMILY, size=18)
        self.font_small = font.Font(family=FONT_FAMILY, size=14)

    def _build_ui(self):
        # Background panel with rounded-rectangle effect
        self.panel = tk.Canvas(self, width=380, height=700, bg=BG, highlightthickness=0)
        self.panel.place(x=20, y=20)

        # Display screen
        disp_frame = tk.Frame(self, bg=BG)
        disp_frame.place(x=38, y=40, width=344, height=120)

        disp_bg = tk.Label(disp_frame, bg=PANEL, bd=0)
        disp_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.display_var = tk.StringVar()
        self.display = tk.Label(
            disp_frame,
            textvariable=self.display_var,
            anchor="e",
            font=self.font_display,
            bg=PANEL,
            fg=TEXT_DARK,
            padx=20,
        )
        self.display.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ON/OFF buttons
        btn_on = tk.Button(self, text="on", font=self.font_small, bg=BTN_GREY,
                           fg=TEXT_DARK, command=self._on_press, relief="flat")
        btn_on.place(x=70, y=180, width=60, height=50)

        btn_off = tk.Button(self, text="off", font=self.font_small, bg=BTN_GREY,
                            fg=TEXT_DARK, command=self._off_press, relief="flat")
        btn_off.place(x=260, y=180, width=60, height=50)

        # Positioning layout for buttons
        start_x = 50
        start_y = 250
        spacing_x = 85
        spacing_y = 78

        # Top utility buttons
        self._make_button("√", lambda: self._action("sqrt"), x=start_x, y=start_y)
        self._make_button("%", lambda: self._action("percent"), x=start_x+spacing_x, y=start_y)
        self._make_button("+/-", lambda: self._action("neg"), x=start_x+2*spacing_x, y=start_y)
        self._make_button("C", lambda: self._action("clear"), x=start_x+3*spacing_x, y=start_y, bg=BTN_CLEAR, fg="black")

        # Main keypad digits and operators
        digits = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("÷", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("×", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("+", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("-", 3, 3),
        ]

        # Create each button dynamically
        for (label, r, c) in digits:
            x = start_x + c * spacing_x
            y = start_y + (r+1) * spacing_y

            if label in ("÷", "×", "+", "-"):
                self._make_button(label, lambda l=label: self._op_press(l),
                                  x=x, y=y, bg=BTN_OP, fg="white")
            elif label == "=":
                self._make_button(label, lambda: self._action("equals"), x=x, y=y)
            elif label == ".":
                self._make_button(label, lambda: self._digit_press("."), x=x, y=y)
            else:
                self._make_button(label, lambda v=label: self._digit_press(v), x=x, y=y, bg=BTN_WHITE, fg=TEXT_DARK)

        # Exponent button
        self._make_button("^", lambda: self._op_press("^"),
                          x=start_x+3*spacing_x, y=start_y+spacing_y, bg=BTN_OP, fg="white")

    def _make_button(self, text, cmd, x, y, w=70, h=60, bg=BTN_GREY, fg="black", font=None):
        # Creates a button and stores reference
        b = tk.Button(self, text=text, command=cmd, bg=bg, fg=fg,
                      bd=0, relief="flat", font=font or self.font_btn)
        b.place(x=x, y=y, width=w, height=h)

        if not hasattr(self, "all_buttons"):
            self.all_buttons = []
        self.all_buttons.append(b)
        return b

    def _digit_press(self, ch):
        # Handle number key presses
        self.calc.input_digit(ch)
        self._update_display()

    def _op_press(self, symbol):
        # Convert GUI symbols into operator characters
        sym_map = {"÷": "/", "×": "*", "+": "+", "-": "-", "^": "^"}
        op = sym_map.get(symbol, symbol)
        self.calc.choose_operator(op)
        self._update_display()

    def _action(self, name):
        # Handle operations like %, sqrt, =, sign toggle, clear
        if name == "sqrt":
            self.calc.apply_sqrt()
        elif name == "percent":
            self.calc.percent()
        elif name == "neg":
            self.calc.toggle_sign()
        elif name == "clear":
            self.calc.clear_entry()
        elif name == "equals":
            self.calc.press_equal()
        self._update_display()

    def _on_press(self):
        # ON button pressed
        if not self.calc.on:
            self.calc.toggle_on_off()
        else:
            self.calc.reset_all()
        self._update_display()
        self._set_buttons_state()

    def _off_press(self):
        # OFF button pressed
        if self.calc.on:
            self.calc.toggle_on_off()
        self._update_display()
        self._set_buttons_state()

    def _set_buttons_state(self):
        # Disable buttons when calculator is OFF
        state = tk.NORMAL if self.calc.on else tk.DISABLED
        for btn in getattr(self, "all_buttons", []):
            btn.config(state=state)

        # ON and OFF buttons must always work
        for child in self.winfo_children():
            try:
                if isinstance(child, tk.Button) and child.cget("text") in ("on", "off"):
                    child.config(state=tk.NORMAL)
            except Exception:
                pass

    def _update_display(self):
        # Update the calculator screen text
        txt = self.calc.current
        if not self.calc.on:
            self.display_var.set("")
        else:
            self.display_var.set(txt)

    def _bind_keys(self):
        # Keyboard input support
        for ch in "0123456789":
            self.bind(ch, self._key_event)
        self.bind(".", self._key_event)
        self.bind("+", self._key_event)
        self.bind("-", self._key_event)
        self.bind("*", self._key_event)
        self.bind("/", self._key_event)
        self.bind("^", self._key_event)

        self.bind("<Return>", lambda e: self._action("equals"))
        self.bind("<BackSpace>", lambda e: (self.calc.backspace(), self._update_display()))
        self.bind("<Escape>", lambda e: (self.calc.clear_entry(), self._update_display()))

        # Shortcuts for %, sqrt, sign toggle
        for key in ("p", "P"):
            self.bind(key, lambda e: (self.calc.percent(), self._update_display()))
        for key in ("s", "S"):
            self.bind(key, lambda e: (self.calc.apply_sqrt(), self._update_display()))
        for key in ("n", "N"):
            self.bind(key, lambda e: (self.calc.toggle_sign(), self._update_display()))

        # Power shortcuts
        self.bind("o", lambda e: self._on_press())
        self.bind("f", lambda e: self._off_press())

    def _key_event(self, event):
        # General key handler
        ch = event.char
        if ch in "0123456789.":
            self._digit_press(ch)
        elif ch in "+-*/^":
            sym_map = {"+": "+", "-": "-", "*": "×", "/": "÷", "^": "^"}
            mapped = sym_map.get(ch, ch)
            if mapped in ("×", "÷", "+", "-", "^"):
                self._op_press(mapped)

# Run the app
if __name__ == "__main__":
    app = CalculatorUI()
    app.mainloop()
