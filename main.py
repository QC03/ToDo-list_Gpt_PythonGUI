import tkinter as tk
import tasks
from ui import TodoUI

def on_close():
    tasks.save_tasks(task_list)
    root.destroy()

if __name__ == "__main__":
    task_list = tasks.load_tasks()

    root = tk.Tk()
    ui = TodoUI(root, task_list, on_close)

    root.mainloop()
