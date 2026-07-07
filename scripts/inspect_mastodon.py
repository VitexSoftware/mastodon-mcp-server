import mastodon
import inspect

client = mastodon.Mastodon(api_base_url='https://example.com')
methods = [
    'status_update', 'status_history', 'status_source', 'status_translate', 
    'conversations', 'scheduled_statuses', 'scheduled_status_update', 
    'scheduled_status_delete', 'notifications_unread_count', 
    'account_lookup', 'status_pin', 'status_unpin', 'status_mute', 
    'status_unmute', 'tag_follow', 'tag_unfollow'
]

for m in methods:
    try:
        sig = inspect.signature(getattr(client, m))
        print(f"{m}: {sig}")
    except Exception as e:
        print(f"{m}: Error getting signature: {e}")