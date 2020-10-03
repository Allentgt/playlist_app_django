import random
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Playlist
from .forms import PlaylistForm


def index(request):
    return render(request, 'index.html')


def thanks(request):
    return render(request, 'thanks.html')


def get_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            playlist = {i: j for i, j in zip(range(10), [form.cleaned_data['song1'], form.cleaned_data['song2'],
                                                         form.cleaned_data['song3'], form.cleaned_data['song4'],
                                                         form.cleaned_data['song5'], form.cleaned_data['song6'],
                                                         form.cleaned_data['song7'], form.cleaned_data['song8'],
                                                         form.cleaned_data['song9'], form.cleaned_data['song10']
                                                         ])}
            data = {'name': form.cleaned_data['name'], 'playlist': playlist}
            p = Playlist(**data)
            p.save()
            return HttpResponseRedirect('/api/thanks/')
    else:
        form = PlaylistForm()

    return render(request, 'playlist.html', {'form': form})


def randomise(request):
    list_dict = {}
    counter = 1
    final_list = []
    while counter < 71:
        list_dict[counter] = [i for i in range(counter, counter + 10)]
        counter += 10
    for i in list_dict.values():
        random.shuffle(i)
        sampling = random.choices(i, k=4)
        final_list.extend(sampling)

    print(list_dict)
    print(len(final_list))
    random.shuffle(final_list)
    print(final_list)
