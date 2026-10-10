from app.models.schemas import Topic


TOPICS = [
    Topic(id="ai-education", title="Should AI tools be allowed in classrooms?"),
    Topic(id="remote-work", title="Is remote work better than office work for young professionals?"),
    Topic(id="climate-tech", title="Can technology solve climate change fast enough?"),
    Topic(id="social-media", title="Does social media do more harm than good?"),
    Topic(id="startup-vs-job", title="Startups vs stable jobs: what should graduates choose?"),
    Topic(id="cashless-india", title="Is India ready to become fully cashless?"),
    Topic(id="four-day-week", title="Should companies adopt a four-day work week?"),
    Topic(id="online-learning", title="Can online learning replace traditional classrooms?"),
    Topic(id="public-transport", title="Should cities prioritize public transport over private cars?"),
    Topic(id="data-privacy", title="Is data privacy more important than convenience?"),
]


def list_topics() -> list[Topic]:
    return TOPICS


def resolve_topic(topic_id: str | None, custom_topic: str | None) -> str:
    if custom_topic and custom_topic.strip():
        return custom_topic.strip()
    for topic in TOPICS:
        if topic.id == topic_id:
            return topic.title
    return TOPICS[0].title
