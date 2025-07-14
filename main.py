import tkinter as tk
import tasks
from ui import TodoUI

def main():
    root = tk.Tk()
    tasks_list = tasks.load_tasks()

    def on_close(task_list):
        tasks.save_tasks(task_list)
        root.destroy()

    TodoUI(root, tasks_list, on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
