'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { LogOut } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

function EditArticleContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const isAuth = localStorage.getItem('cms_auth');
    if (isAuth !== 'true') {
      router.push('/login');
    } else {
      setIsChecking(false);
    }
  }, [router]);
  
  const [article, setArticle] = useState<any>(null);
  const [form, setForm] = useState({
    title_en: '',
    content_en: '',
    category: '',
    meta_description: '',
    keywords: '',
    hashtags: '',
    naver_tv_url: ''
  });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('cms_auth');
    router.push('/login');
  };

  useEffect(() => {
    if (!id) return;
    
    fetch(`${API_URL}/api/article/${id}`)
      .then(res => res.json())
      .then(data => {
        setArticle(data);
        setForm({
          title_en: data.title || '',
          content_en: data.content || '',
          category: data.category || '',
          meta_description: data.meta_description || '',
          keywords: data.keywords || '',
          hashtags: data.hashtags || '',
          naver_tv_url: data.naver_tv_url || ''
        });
      });
  }, [id]);

  async function handleSave() {
    if (!id) return;
    setSaving(true);
    
    try {
      const response = await fetch(`${API_URL}/api/update-article`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          news_id: id,
          updates: {
            title_en: form.title_en,
            content_en: form.content_en,
            category: form.category,
            meta_description: form.meta_description,
            keywords: form.keywords,
            hashtags: form.hashtags,
            naver_tv_url: form.naver_tv_url
          }
        })
      });
      
      if (response.ok) {
        alert('✅ Article updated successfully!');
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      alert('❌ Failed to save. Please try again.');
      console.error(error);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!id) return;
    if (!confirm('⚠️ Are you sure you want to delete this article? This cannot be undone.')) return;
    
    setDeleting(true);
    try {
      const response = await fetch(`${API_URL}/api/delete-article`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ news_id: id })
      });
      
      if (response.ok) {
        alert('✅ Article deleted successfully!');
        router.push('/articles');
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      alert('❌ Failed to delete. Please try again.');
      console.error(error);
    } finally {
      setDeleting(false);
    }
  }

  if (isChecking) return <div className="p-8">Loading...</div>;
  if (!id) return <div className="p-8">No article ID provided</div>;
  if (!article) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Edit Article</h1>
          <div className="flex gap-2">
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
            <button 
              onClick={handleDelete}
              disabled={deleting || saving}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </button>
            <button
              onClick={() => router.push('/articles')}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Back to Articles
            </button>
            <button 
              onClick={handleSave} 
              disabled={saving || deleting}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">News ID</label>
            <input
              type="text"
              value={article.news_id}
              disabled
              className="w-full px-4 py-2 border rounded bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Title</label>
            <input
              type="text"
              value={form.title_en}
              onChange={e => setForm({...form, title_en: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Category</label>
            <select
              value={form.category}
              onChange={e => setForm({...form, category: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            >
              <option value="경제">경제</option>
              <option value="IT_과학">IT_과학</option>
              <option value="정치">정치</option>
              <option value="사회">사회</option>
              <option value="문화">문화</option>
              <option value="스포츠">스포츠</option>
              <option value="국제">국제</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={form.content_en}
              onChange={e => setForm({...form, content_en: e.target.value})}
              rows={20}
              className="w-full px-4 py-2 border rounded font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Meta Description</label>
            <textarea
              value={form.meta_description}
              onChange={e => setForm({...form, meta_description: e.target.value})}
              rows={3}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Keywords</label>
            <input
              type="text"
              value={form.keywords}
              onChange={e => setForm({...form, keywords: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Hashtags</label>
            <input
              type="text"
              value={form.hashtags}
              onChange={e => setForm({...form, hashtags: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Naver TV Video URL</label>
            <input
              type="url"
              value={form.naver_tv_url}
              onChange={e => setForm({...form, naver_tv_url: e.target.value})}
              placeholder="https://tv.naver.com/v/12345678"
              className="w-full px-4 py-2 border rounded"
            />
            <p className="text-sm text-gray-500 mt-1">Enter Naver TV video URL (optional)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EditArticle() {
  return (
    <Suspense fallback={<div className="p-8">Loading...</div>}>
      <EditArticleContent />
    </Suspense>
  );
}
