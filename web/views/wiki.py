from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from web.forms.wiki import WikiModelForm
from web import models


def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id.isdigit():
        pass

    if request.GET.get('wiki_id'):
        article = models.WikiArticle.objects.filter(id=request.GET.get('wiki_id'), project_id=project_id).first()
        return render(request, 'manage/wiki.html', {'article': article})

    return render(request, 'manage/wiki.html')


def wiki_add(request, project_id):
    form = WikiModelForm(request=request)
    if request.method == 'POST':
        form = WikiModelForm(request=request, data=request.POST)
        if form.is_valid():
            form.instance.project_id = project_id

            form.instance.depth = form.instance.parent_wiki.depth + 1
            form.save()
            return redirect(reverse('wiki', kwargs={'project_id': request.project.id}))
        else:
            return render(request, 'manage/wiki_add.html', {'form': form, 'error': form.errors})

    return render(request, 'manage/wiki_add.html', {'form': form})


def wiki_menu(request, project_id):
    # 在获取的文章没有进行排序之前 如果先定义的子级文章修改了所属父级文章 那么在文章渲染的时候 就不会显示
    # 所以通过添加字段depth 进行排序 那么即使是后定义的父级文章 也会先进行渲染
    articles = models.WikiArticle.objects.filter(project_id=project_id).values('id', 'title', 'parent_wiki_id').order_by('id', 'depth')

    return JsonResponse({'articles': list(articles)})
