
from django.contrib import messages
from django.shortcuts import render
from musicbeats.models import Song, Watchlater, History, Channel
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When

def search(request):
    query = request.GET.get("query")
    song = Song.objects.all()
    qs = song.filter(name__icontains=query)
    return render(request, 'musicbeats/search.htm', {"songs":qs, "query":query})

def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST['music_id']
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/musicbeats/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, 'musicbeats/history.htm', {"history": song})

def watchlater(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST['video_id']

        
        if not user.is_authenticated:
            return redirect("login")

        else: 
            watch = Watchlater.objects.filter(user=user)
            for i in watch:
                if video_id == i.video_id:
                    message = "Your Video is Already Added"
                    break
                else:
                    watchlater = Watchlater(user=user, video_id=video_id)
                    watchlater.save()
                    message = "Your Video is Succesfully Added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(request, f"musicbeats/songpost.htm", {'song': song, "message": message})

    wl = Watchlater.objects.filter(user=request.user)
    ids = []
    for i in wl:
        ids.append(i.video_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "musicbeats/watchlater.htm", {'song': song})
        
def songs(request):
    song = Song.objects.all()
    return render(request, 'musicbeats/songs.htm', {'song': song})

def songpost(request, id):
    song = Song.objects.filter(song_id=id).first()
    return render(request, 'musicbeats/songpost.htm', {'song': song})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
    

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("/")

        else:
            messages.info(request, 'Wrong Username or Password!')
            return redirect("login")
    else:   
        return render(request, 'musicbeats/login.htm')

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Please try another one!")
            return redirect("signup")

        if len(username) > 15:
            messages.error(request, "Username must be less than 15 characters")
            return redirect("signup")
        
        if not username.isalnum():
            messages.error(request, "Username should only contain Letters and Numbers.")
            return redirect("signup")

             

        if pass1 != pass2:
            messages.info(request, "Password Did not Match. Please Sign Up Again!")
            return redirect("signup")




            
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        user = authenticate(username=username, password=pass1)
        from django.contrib.auth import login
        login(request, user)

        channel = Channel(name=username)
        channel.save()

        return redirect('/')

    return render(request, 'musicbeats/signup.htm')

def logout_user(request):
    logout(request)
    return redirect("/")

def channel(request, channel):
    chan = Channel.objects.filter(name=channel).first()
    video_ids = str(chan.music).split(" ")[1:]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
    song = Song.objects.filter(song_id__in=video_ids).order_by(preserved)    

    return render(request, "musicbeats/channel.htm", {"channel": chan, "song": song})

def upload(request):
    if request.method == "POST":
        name = request.POST['name']
        singer = request.POST['singer']
        #tag = request.POST['tag']
        image1 = request.FILES['img']
        #movie = request.POST['movie']
        #credit = request.POST['credit']
        song1 = request.FILES['file']

        song_model = Song(name=name, singer=singer,   image=image1,  song=song1)
        song_model.save()

        music_id = song_model.song_id
        channel_find = Channel.objects.filter(name=str(request.user))
        print(channel_find)

        for i in channel_find:
            i.music += f" {music_id}"
            i.save()

        return redirect("/")

    return render(request, "musicbeats/upload.htm")
