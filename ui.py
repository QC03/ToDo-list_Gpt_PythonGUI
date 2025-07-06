import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import tasks

bgColor = "#1f1f1f"
frColor = "#D8D8D8"

class TodoUI:
    def __init__(self, root, tasks_list, on_close):
        self.root = root
        self.tasks = tasks_list
        self.on_close = on_close

        self.root.title("할 일 목록 (D-day 포함)")
        self.root.geometry("500x850")

        # 마지막 위치 불러와 적용
        self.rX, self.rY = tasks.load_window_pos()
        self.rWidth = 500
        self.rHeight = 850
        self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")

        self.root.resizable(False, False)
        self.move_locked = True  # 초기에는 위치 고정

        # 위치 고정 관련 바인딩
        self.root.bind("<Configure>", self.on_configure)

        # 입력 영역
        frame_input = tk.Frame(root)
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="할 일:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_task = tk.Entry(frame_input, width=30, font=("맑은 고딕", 12))
        self.entry_task.grid(row=0, column=1, padx=5, pady=2)

        btn_check_calendar = tk.Button(frame_input, text="날짜선택 토글", command=self.toggle_calendar)
        btn_check_calendar.grid(row=1, column=0, padx=5, pady=2)
        self.calendar_locked = True # 초기에는 날짜미선택

        self.entry_date = DateEntry(
            frame_input, 
            width=27, 
            background= bgColor, 
            foreground= frColor, 

            normalbackground= "#313131",
            normalforeground= "#BDBDBD",
            weekendbackground= "#313131",
            weekendforeground= "#BDBDBD",
            othermonthbackground="#BDBDBD",
            othermonthforeground="#636363",

            headersbackground= bgColor,
            headersforeground= frColor,

            bordercolor="white",
            borderwidth=1, 
            date_pattern='yyyy-mm-dd', 
            state="readonly",
            firstweekday="sunday")
        
        self.entry_date.grid(row=1, column=1, padx=5, pady=2)
        self.entry_date.set_date(datetime.today())
        self.entry_date.configure(state="disabled")

        btn_add = tk.Button(frame_input, text="추가", command=self.add_task)
        btn_add.grid(row=2, column=0, columnspan=2, pady=8)

        # 위치 고정 토글 버튼
        self.btn_toggle_move = tk.Button(root, text="위치 이동 허용", command=self.toggle_move)
        self.btn_toggle_move.pack(pady=5)

        # 버튼 영역 (완료, 삭제)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="완료 토글", command=self.mark_done, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="삭제", command=self.delete_task, width=12).pack(side=tk.LEFT, padx=10)

        # 리스트 캔버스 및 라벨
        tk.Label(root, text="오늘 해야 할 일", font=("맑은 고딕", 12, "bold")).pack()
        self.today_canvas = tk.Canvas(root, width=460, height=160, bg="white")
        self.today_canvas.pack(pady=5)

        tk.Label(root, text="날짜 미지정 할 일", font=("맑은 고딕", 12, "bold")).pack()
        self.no_date_canvas = tk.Canvas(root, width=460, height=160, bg="white")
        self.no_date_canvas.pack(pady=5)

        tk.Label(root, text="미래 할 일 (D-n)", font=("맑은 고딕", 12, "bold")).pack()
        self.future_canvas = tk.Canvas(root, width=460, height=270, bg="white")
        self.future_canvas.pack(pady=5)

        self.update_lists()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def toggle_calendar(self):
        self.calendar_locked = not self.calendar_locked
        if self.calendar_locked:
            self.entry_date.configure(state="disabled")
        else:
            self.entry_date.configure(state="enable")

    def toggle_move(self):
        self.move_locked = not self.move_locked
        if self.move_locked:
            self.btn_toggle_move.config(text="위치 이동 허용")
            # 위치 고정 즉시 적용
            self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")
        else:
            self.btn_toggle_move.config(text="위치 이동 금지")

    def on_configure(self, event):
        if self.move_locked:
            # 창 위치가 바뀌면 강제로 원래 위치로 되돌림
            x, y = self.root.winfo_x(), self.root.winfo_y()
            if (x, y) != (self.rX, self.rY):
                self.root.geometry(f"{self.rWidth}x{self.rHeight}+{self.rX}+{self.rY}")
        else:
            # 위치 이동 허용 시 위치 저장
            self.rX = self.root.winfo_x()
            self.rY = self.root.winfo_y()

    def add_task(self):
        task_text = self.entry_task.get().strip()
        if not task_text:
            messagebox.showwarning("입력 오류", "할 일을 입력하세요.")
            return

        date_val = None
        try:
            date_val = self.entry_date.get_date()
        except:
            pass

        if not self.calendar_locked:
            date_str = date_val.strftime("%Y-%m-%d") if date_val else None
        else:
            date_str = "1900-01-01"

        self.tasks.append({"task": task_text, "date": date_str, "done": False})
        self.entry_task.delete(0, tk.END)
        self.entry_date.set_date(datetime.today())

        self.update_lists()

    def d_day_str(self, d):
        if d == 0:
            return "D-day"
        elif d > 0:
            return f"D-{d}"
        else:
            return f"D+{-d}"

    def update_lists(self):
        self.today_canvas.delete("all")
        self.no_date_canvas.delete("all")
        self.future_canvas.delete("all")

        today = datetime.today()
        y_offset = 10
        box_height = 24
        padding = 8

        # 오늘 해야 할 일
        y = y_offset
        for t in self.tasks:
            if t.get("date") == today.strftime("%Y-%m-%d"):
                text = ("[완료] " if t.get("done") else "") + t["task"]
                self.today_canvas.create_text(10, y, anchor="nw", text=text, font=("맑은 고딕", 12))
                y += box_height + padding

        # 날짜 미지정 할 일
        y = y_offset
        for t in self.tasks:
            if t.get("date") == "1900-01-01":
                text = ("[완료] " if t.get("done") else "") + t["task"]
                self.no_date_canvas.create_text(10, y, anchor="nw", text=text, font=("맑은 고딕", 12))
                y += box_height + padding

        # 미래 할 일 (D-n)
        y = y_offset
        for t in self.tasks:
            if t.get("date"):
                try:
                    dt = datetime.strptime(t["date"], "%Y-%m-%d")
                except:
                    continue
                delta = (dt - today).days + 1
                if delta > 0:
                    d_str = self.d_day_str(delta)
                    text = ("[완료] " if t.get("done") else "") + t["task"]
                    color = "gray"
                    if delta == 1:
                        color = "red"
                    elif delta == 2:
                        color = "orange"
                    elif delta == 3:
                        color = "green"
                    else:
                        color = "black"
                    self.future_canvas.create_rectangle(5, y, 25, y + box_height - 6, outline=color, width=2)
                    self.future_canvas.create_text(30, y, anchor="nw", text=f"{d_str} {text}", font=("맑은 고딕", 12))
                    y += box_height + padding

    def mark_done(self):
        if not self.tasks:
            messagebox.showinfo("알림", "할 일이 없습니다.")
            return
        # 임시: 가장 최근 할 일 완료 토글
        self.tasks[0]["done"] = not self.tasks[0].get("done", False)
        self.update_lists()

    def delete_task(self):
        if not self.tasks:
            messagebox.showinfo("알림", "삭제할 할 일이 없습니다.")
            return
        self.tasks.pop(0)
        self.update_lists()

    def close(self):
        # 창 위치 저장
        tasks.save_window_pos(self.root.winfo_x(), self.root.winfo_y())
        self.on_close()
