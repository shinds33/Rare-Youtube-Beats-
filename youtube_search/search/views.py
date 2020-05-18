import requests

from isodate import parse_duration
from django.conf import settings
from django.shortcuts import render, redirect


def index(request):
    our_videos = []

    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part' : 'snippet',
            'q' : request.POST['search'],
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'maxResults' : 5000,
            'type' : 'video'

        }

        our_request = requests.get(search_url, params=search_params)
        results = our_request.json()['items']

        video_ids = []

        for result in results:
            video_ids.append(result['id']['videoId'])

        # Handling "Generic" im feeling lucky request
        if request.POST['submit'] == 'lucky':
            return redirect(f'https://www.youtube.com/watch?v={ video_ids[0] }')

        # Handling "Rare request
        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails,statistics',
            'id' : ','.join(video_ids),
            'maxResults': 5000
        }
        our_request = requests.get(video_url, params=video_params)
        results = our_request.json()['items']

        for current_result in results:
            video_data = {
                'title' : current_result['snippet']['title'],
                'id' : current_result['id'],
                'url' : f'https://www.youtube.com/watch?v={ current_result["id"] }',
                'duration' : parse_duration(current_result['contentDetails']['duration']),
                'thumbnail' : current_result['snippet']['thumbnails']['high']['url'],
                'views' : current_result['statistics']['viewCount'],
                'dislikes' : current_result['statistics']['dislikeCount']
            }

            # Collecting our relevant search results
            test_title = video_data['title']
            test_views = int(video_data['views'])
            test_dl = int(video_data['dislikes'])
            if any(keywords in test_title for keywords in ('free', 'Free', 'FREE', '(FREE)', '[FREE]')):
                if (2000 < test_views < 5000) and (test_dl < 2):
                    print(' ')
                    print(video_data['url'])
                    our_videos.append(video_data)

    context = {
        'videos' : our_videos
    }

    return render(request, 'search/index.html', context)


