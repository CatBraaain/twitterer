from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    Task,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()


class ScrapingProgress(Progress):
    task_id: TaskID
    task: Task
    url: str

    def __init__(self, url: str, max_tweet_count: int) -> None:
        super().__init__(
            TextColumn("[cyan]{task.description}[/cyan]"),
            SpinnerColumn("simpleDotsScrolling"),
            TimeElapsedColumn(),
        )
        self.start()
        self.task_id = self.add_task(
            f"Scraping 0/{max_tweet_count} tweets", total=max_tweet_count
        )
        self.task = self.tasks[self.task_id]
        self.url = url

    def advance_scraping(self) -> None:
        self.update(
            task_id=self.task_id,
            advance=1,
            description=f"Scraping {self.task.completed}/{self.task.total} tweets",
        )

    def stop_on_got_enough(self) -> None:
        self.update(
            self.task_id,
            description=f"Scraped {self.task.completed}/{self.task.total} tweets",
        )
        self.stop()
        console.print(
            f"Successfully got the specified number of tweets in [link]{self.url}[/link]"
        )

    def stop_on_got_all(self) -> None:
        self.update(
            self.task_id,
            description=f"Scraped {self.task.completed}/{self.task.completed}({self.task.total}) tweets",
        )
        self.stop()
        console.print(f"Successfully got all tweets in [link]{self.url}[/link]")
