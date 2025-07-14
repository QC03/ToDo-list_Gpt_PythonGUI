import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import tasks

bgColor = "#ADD8E6"
fgColor = "#4B89DC"
list_bg = "#DAE5E9"

btn_Font = ("온글잎 박다현체 Regular", 14)
lbl_Font = ("온글잎 박다현체 Regular", 20)
ipt_Font = ("온글잎 박다현체 Regular", 14)

class TodoUI:
    def __init__(self, root, tasks_list, on_close):
        self.root = root
        self.tasks = tasks_list
        self.on_close = on_close

        self.root.title("To-Do List")
        self.rX, self.rY = tasks.load_window_pos()
        self.rWidth = 500
        self.rHeight = 900
        self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")
        self.root.configure(bg=bgColor)
        self.root.resizable(False, False)
        self.move_locked = True
        self.root.bind("<Configure>", self.on_configure)

        # 입력 영역
        input_frame = tk.Frame(root, bg=bgColor)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="할 일:", bg=bgColor, fg=fgColor, font=lbl_Font).grid(row=0, column=0)
        self.entry_task = tk.Entry(input_frame, width=25, font=ipt_Font,
                                   bg=list_bg, fg=fgColor, insertbackground=fgColor)
        self.entry_task.grid(row=0, column=1)

        self.calendar_locked = True
        tk.Button(input_frame, text="날짜 선택", font=btn_Font,
                  width=12, height=1, command=self.toggle_calendar).grid(row=1, column=0, pady=10)

        self.entry_date = DateEntry(
            input_frame, width=30, date_pattern='yyyy-mm-dd',
            background=bgColor, foreground=fgColor,
            normalbackground=list_bg, normalforeground=fgColor,
            weekendbackground=list_bg, weekendforeground=fgColor,
            headersbackground=bgColor, headersforeground=fgColor,
            bordercolor="white", state="readonly", firstweekday="sunday"
        )
        self.entry_date.set_date(datetime.today())
        self.entry_date.configure(state="disabled")
        self.entry_date.grid(row=1, column=1, padx=5, pady=10)

        tk.Button(input_frame, text="할 일 추가", padx="10", font=btn_Font, width=15, height=1, command=self.add_task).grid(row=2, column=0, columnspan=2, pady=5)

        self.btn_toggle_move = tk.Button(root, text="위치 이동 허용", padx="10", font=btn_Font, width=15, height=1, command=self.toggle_move)
        self.btn_toggle_move.pack(pady=10)

        # 리스트 영역
        self.listboxes = {}

        for name, title in zip(["today", "no_date", "future"],
                               ["†오늘 해야 할 일†", "†날짜 미지정 할 일†", "†미래 할 일†"]):
            tk.Label(root, text=title, bg=bgColor, fg=fgColor, font=lbl_Font).pack()
            lb = tk.Listbox(root, width=60, height=8, font=ipt_Font,
                            bg=list_bg, fg=fgColor, selectbackground="#B0C5CC", activestyle="none")
            lb.pack(pady=(0, 10))
            self.listboxes[name] = lb

        # 버튼 영역
        btn_frame = tk.Frame(root, bg=bgColor)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="완료", font=btn_Font, command=self.mark_done, width=15, height=1).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="삭제", font=btn_Font, command=self.delete_task, width=15, height=1).pack(side=tk.LEFT, padx=10)

        self.update_listboxes()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def toggle_calendar(self):
        self.calendar_locked = not self.calendar_locked
        self.entry_date.configure(state="disabled" if self.calendar_locked else "readonly")

    def toggle_move(self):
        self.move_locked = not self.move_locked
        self.btn_toggle_move.config(text="위치 이동 허용" if self.move_locked else "위치 이동 금지")
        if self.move_locked:
            self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")

    def on_configure(self, event):
        if self.move_locked:
            if (event.x, event.y) != (self.rX, self.rY):
                self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")
        else:
            self.rX = self.root.winfo_x()
            self.rY = self.root.winfo_y()

    def add_task(self):
        text = self.entry_task.get().strip()
        if not text:
            messagebox.showwarning("입력 오류", "할 일을 입력하세요.")
            return
        date = self.entry_date.get_date().strftime("%Y-%m-%d") if not self.calendar_locked else "1900-01-01"
        self.tasks.append({"task": text, "date": date, "done": False})
        self.entry_task.delete(0, tk.END)
        self.update_listboxes()

    def get_d_day_color(self, delta):
        if delta == 1:
            return "red"
        elif delta == 2:
            return "orange"
        elif delta == 3:
            return "green"
        return fgColor

    def update_listboxes(self):
        for lb in self.listboxes.values():
            lb.delete(0, tk.END)

        today = datetime.today().date()

        for idx, t in enumerate(self.tasks):
            date_str = t["date"]
            done = "[완료] " if t["done"] else " ♤ "
            label = f"{done}{t['task']}"

            if date_str == "1900-01-01":
                self.listboxes["no_date"].insert(tk.END, label)
            else:
                try:
                    task_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    delta = (task_date - today).days
                    if delta == 0:
                        self.listboxes["today"].insert(tk.END, label)
                    elif delta > 0:
                        d_label = f"D-{delta} {label}"
                        self.listboxes["future"].insert(tk.END, d_label)
                    else:
                        d_label = f"D+{abs(delta)} {label}"
                        self.listboxes["future"].insert(tk.END, d_label)
                except:
                    self.listboxes["no_date"].insert(tk.END, label)

    def get_selected_index(self):
        for key, lb in self.listboxes.items():
            if lb.curselection():
                return key, lb.curselection()[0]
        return None, None

    def mark_done(self):
        key, idx = self.get_selected_index()
        if key is None:
            return
        matching_tasks = self.get_tasks_by_list_type(key)
        if idx < len(matching_tasks):
            matching_tasks[idx]["done"] = not matching_tasks[idx]["done"]
            self.update_listboxes()

    def delete_task(self):
        key, idx = self.get_selected_index()
        if key is None:
            return
        
        matching_tasks = self.get_tasks_by_list_type(key)
        for i, t in enumerate(self.tasks):
            if(t["task"] != matching_tasks[idx]["task"] or
                t["date"] != matching_tasks[idx]["date"] or
                t["done"] != matching_tasks[idx]["done"]):
                continue

            del self.tasks[i]
            break

        self.tasks = self.flatten_all_tasks()
        self.update_listboxes()

    def get_tasks_by_list_type(self, list_type):
        today = datetime.today().date()
        filtered = []
        for t in self.tasks:
            try:
                date = datetime.strptime(t["date"], "%Y-%m-%d").date() if t["date"] != "1900-01-01" else None
                delta = (date - today).days if date else None
            except:
                delta = None

            if list_type == "today" and date == today:
                filtered.append(t)
            elif list_type == "no_date" and t["date"] == "1900-01-01":
                filtered.append(t)
            elif list_type == "future" and delta:
                filtered.append(t)
        return filtered

    def flatten_all_tasks(self):
        all = []
        for key in self.listboxes:
            all += self.get_tasks_by_list_type(key)
        return all

    def close(self):
        tasks.save_window_pos(self.root.winfo_x(), self.root.winfo_y())
        self.on_close(self.tasks)
