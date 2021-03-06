from django.shortcuts import render, get_object_or_404, redirect
from cms.note import Note, Image
from cms.qiita import Qiita
from cms.models import Activity, Techblog
from cms.forms import ActivityForm, TechblogForm
from django.contrib.auth.decorators import login_required

@login_required
def top(request):
    return render(request, 'cms/top.html',)

# -------------------------------Activity
@login_required
def activity_list(request):
    # 記事の一覧
    # return HttpResponse('記事の一覧')
    activities = Activity.objects.all().order_by('id')

    return render(request, 'cms/activity_list.html', {'activities': activities})

@login_required
def activity_update(request, activity_id):
    activity = Activity()
    note = Note()
    # DBから取得
    activity = get_object_or_404(Activity, pk=activity_id)
    # Noteから取得
    note_activity =  note.get_note(activity.note_item_id)
    activity.title        = note_activity['name']
    activity.body         = Image.rewriting_img_path(note_activity['body'], note_activity['key'])
    activity.image        = Image.rename_eyecatch(note_activity['eyecatch'], note_activity['key'])
    activity.save()
    return redirect('cms:activity_list')

@login_required
def activity_edit(request, activity_id=None):
    # 記事の編集
    if activity_id:   # activity_id が指定されている (修正時)
        activity = get_object_or_404(Activity, pk=activity_id)
    else:         # activity_id が指定されていない (追加時)
        activity = Activity()
    if request.method == 'POST':
        # POST された request データからフォームを作成
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():    # フォームのバリデーション
            activity = form.save(commit=False)
            activity.image = request.FILES['image']
            activity.save()
            return redirect('cms:activity_list')
    else:    # GET の時
        form = ActivityForm(instance=activity)  # activity インスタンスからフォームを作成

    return render(request, 'cms/activity_edit.html', dict(form=form, activity_id=activity_id))

@login_required
def activity_del(request, activity_id):
    # 記事の削除
    activity = get_object_or_404(Activity, pk=activity_id)
    activity.delete()
    return redirect('cms:activity_list')



@login_required
def note_add(request):
    note = Note()
    note_list = note.get_deta()
    registered_note_item_id = Activity.objects.exclude(
        note_item_id=None).values_list('note_item_id', flat=True)
    for n in note_list:
        note_item_id = n["key"]
    # note_item_id = "ne40b6a301258"
        if note_item_id not in registered_note_item_id:
            note_activity = note.get_note(note_item_id)
            activity = Activity()
            activity.title        = note_activity['name']
            activity.body         = Image.rewriting_img_path(note_activity['body'], note_activity['key'])
            activity.note_item_id = note_item_id
            activity.image        = Image.rename_eyecatch(note_activity['eyecatch'], note_activity['key'])
            activity.is_note      = True
            activity.save()
    return redirect('cms:activity_list')


# -------------------------------techblog
@login_required
def techblog_list(request):
    techblogs = Techblog.objects.all().order_by('id')
    return render(request, 'cms/techblog_list.html', {'techblogs': techblogs})

@login_required
def techblog_edit(request, techblog_id=None):
    # 記事の編集
    if techblog_id:   # techblog_id が指定されている (修正時)
        techblog = get_object_or_404(Techblog, pk=techblog_id)
    else:         # techblog_id が指定されていない (追加時)
        techblog = Techblog()
    if request.method == 'POST':
        # POST された request データからフォームを作成
        form = TechblogForm(request.POST, instance=techblog)
        if form.is_valid():    # フォームのバリデーション
            techblog = form.save(commit=False)
            try:
                techblog.image = request.FILES['image']
            except KeyError:
                pass
            techblog.save()
            return redirect('cms:techblog_list')
    else:    # GET の時
        form = TechblogForm(instance=techblog)  # techblog インスタンスからフォームを作成

    return render(request, 'cms/techblog_edit.html', dict(form=form, techblog_id=techblog_id))

@login_required
def techblog_del(request, techblog_id):
    # 記事の削除
    techblog = get_object_or_404(Techblog, pk=techblog_id)
    qiita = Qiita()
    qiita.delete_post_related_images(techblog)
    techblog.delete()
    return redirect('cms:techblog_list')

@login_required
def qiita_add(request):
    qiita = Qiita()
    qiita_user_ids = qiita.get_qiita_user_ids()
    posts = qiita.get_posts(qiita_user_ids)
    qiita.import_qiita(posts)
    return redirect('cms:techblog_list')
