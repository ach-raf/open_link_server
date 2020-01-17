import requests


def get_youtube_info(link):
    """this function extract youtube title from a link"""

    api_key = "AIzaSyAgwoZA34QfntXClfsk2UhyZKLG9G6g4PU"

    # https://m.youtube.com/watch?v=J4YPMiFaPWo
    if 'm.' in link:
        link = link.replace('m', 'www')
    if 'www' in link:
        link = link[: 43]  # 43 length of a normal youtube video example https://www.youtube.com/watch?v=_ft2Ac1hENM
        link = 'https://youtu.be/' + link[len(link) - 11:]  # 11 length of the youtube id code example _ft2Ac1hENM

    link = link[: 28]  # 28 length of the shrank youtube url example https://youtu.be/8tbP3f3i03E
    video_id = link[len(link) - 11:]
    # url = 'https://www.youtube.com/watch?v=' + video_id
    # params = {'format': 'json', 'url': url}
    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/videos?key={}&part=snippet&id={}"
                                .format(api_key, video_id))
        # response = requests.get('https://noembed.com/embed', params=params)
        data = response.json()
        return data['items'][0]['snippet']['title']
    except IndexError:
        return link + " DELETED"
