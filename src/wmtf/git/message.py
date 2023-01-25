from transformers import AutoModelWithLMHead, SummarizationPipeline, AutoTokenizer
import requests
from nltk.tokenize import WordPunctTokenizer
import nltk
import shutup
import string
from wmtf.wm.models import TaskInfo


class MessageMeta(type):

    _instance: "Message" = None
    _path: str = (
        "SEBIS/code_trans_t5_small_commit_generation_transfer_learning_finetune"
    )
    _pipeline = None
    _model = None
    _tokenizer = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    @property
    def tokenizer(cls):
        if not cls._tokenizer:
            cls._tokenizer = AutoTokenizer.from_pretrained(cls._path)
        return cls._tokenizer

    @property
    def model(cls):
        if not cls._model:
            cls._model = AutoModelWithLMHead.from_pretrained(cls._path)
        return cls._model

    @property
    def pipeline(cls):
        return SummarizationPipeline(model=cls.model, tokenizer=cls.tokenizer)

    def summarize(cls, diff: str) -> str:
        tr = str.maketrans("", "", string.punctuation)
        nltk.download("punkt", quiet=True)
        tokenized_list = WordPunctTokenizer().tokenize(diff.translate(tr))
        diff = " ".join(tokenized_list[:1000])
        return cls().doSummarize(diff)

    def random(cls) -> str:
        return cls().getRandom()

    def branch(cls, task: TaskInfo) -> str:
        return cls().branchMessage(task)


class Message(object, metaclass=MessageMeta):
    def doSummarize(self, changes: str) -> str:
        with shutup.mute_warnings:
            res = __class__.pipeline([changes])
            return res[0]["summary_text"].split(".")[0].strip()

    def getRandom(self) -> str:
        req = requests.get("https://commit.cacko.net/index.txt")
        return req.content.decode().strip()

    def branchMessage(self, task: TaskInfo) -> str:
        tr = str.maketrans("", "", string.punctuation)
        return f"({task.id}) {(task.summary.translate(tr)):.40}".strip()
