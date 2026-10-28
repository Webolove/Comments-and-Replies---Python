import threading
import time
import copy

class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

class CommentService:
    def __init__(self, post_store):
        self.post_store = post_store
        # TODO: Initialize your data structures and concurrency controls here.
        
        self.comment_count: int = 0
        self.reply_count: int = 0
        
        self.all_comments: dict[int, dict[int, object]] = {}
        
        self._lock = threading.Lock()
    
    def is_valid(self, val: str):
        if val is None or (not isinstance(val, str)):
            return False
        
        isNotSpace = False
        for i in val:
            if i != ' ':
                isNotSpace = True
                break
            
        return isNotSpace

    def add_comment(self, post_id: int, user_id: str, content: str) -> dict:
        """
        Create a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "user_id": str,
            "content": str,
            "created_at": float,
            "replies": []
        }

        Raises NotFoundError if post_id does not exist.
        Raises ValidationError if user_id or content is empty.
        """
        with self._lock:
            if not self.is_valid(user_id) or not self.is_valid(content):
                raise ValidationError
            
            if not self.post_store.exists(post_id):
                raise NotFoundError
            
            last_id = self.comment_count
            
            new_id = last_id + 1
            self.comment_count = new_id
            
            comment = {
                "id": new_id,
                "post_id": post_id,
                "user_id": user_id,
                "content": content,
                "created_at": time.time(),
                "replies": []
            }
            
            self.all_comments.setdefault(post_id, {})[new_id] = comment
            return copy.deepcopy(comment)
        # pass

    def add_reply(self, post_id: int, comment_id: int, user_id: str, content: str) -> dict:
        """
        Create a reply to a comment and return its dictionary representation:

        {
            "id": int,
            "post_id": int,
            "comment_id": int,
            "user_id": str,
            "content": str,
            "created_at": float
        }

        Raises NotFoundError if post_id does not exist.
        Raises NotFoundError if comment_id does not exist for the given post.
        Raises ValidationError if user_id or content is empty.
        """
        with self._lock:
            if not self.is_valid(user_id) or not self.is_valid(content):
                raise ValidationError
            
            if not self.post_store.exists(post_id):
                raise NotFoundError
            
            post_comments = self.all_comments.get(post_id, {})
            
            if comment_id not in post_comments:
                raise NotFoundError
            
            last_id = self.reply_count
            new_id = last_id + 1
            
            self.reply_count = new_id
            
            reply = {
                "id": new_id,
                "post_id": post_id,
                "comment_id": comment_id,
                "user_id": user_id,
                "content": content,
                "created_at": time.time()
            }
            
            self.all_comments[post_id][comment_id]["replies"].append(reply)
            
            ans = copy.deepcopy(reply)
            return ans
        

    def get_comments(self, post_id: int) -> list:
        """
        Return all comments for the given post.

        Each comment must include its "replies" list.
        Comments and replies must be returned in creation order.

        Raises NotFoundError if post_id does not exist.
        """        
        with self._lock:
            if post_id is None or not self.post_store.exists(post_id):
                raise NotFoundError
            
            post_comments: list = []
            
            myDict = self.all_comments.get(post_id, {})
            for key, value in myDict.items():
                post_comments.append([int(key), value])
            
            post_comments.sort()
            n = len(post_comments)
            
            ans: list = []
            for i in range(n):
                ans.append(post_comments[i][1])
        
            return copy.deepcopy(ans)
        # pass
