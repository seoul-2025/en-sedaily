'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Settings, Save, ArrowLeft, Video, Calendar, Info, CheckCircle, AlertCircle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

export default function SettingsPage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [naverTvUrl, setNaverTvUrl] = useState('');
  const [effectiveDate, setEffectiveDate] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const isAuth = localStorage.getItem('cms_auth');
    if (isAuth !== 'true') {
      router.push('/login');
    } else {
      setIsChecking(false);
    }
  }, [router]);

  useEffect(() => {
    if (!isChecking) {
      fetchSettings();
    }
  }, [isChecking]);

  async function fetchSettings() {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/admin/settings`);
      if (response.ok) {
        const data = await response.json();
        setNaverTvUrl(data.naver_tv_url || '');
        setEffectiveDate(data.effective_date || getTodayDate());
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      setEffectiveDate(getTodayDate());
    } finally {
      setLoading(false);
    }
  }

  function getTodayDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  async function handleSave() {
    if (!naverTvUrl.trim()) {
      setMessage({ type: 'error', text: 'Please enter a Naver TV URL' });
      return;
    }

    if (!effectiveDate) {
      setMessage({ type: 'error', text: 'Please select an effective date' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_URL}/admin/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          naver_tv_url: naverTvUrl,
          effective_date: effectiveDate
        })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: '✅ Settings saved successfully! New articles will use this video URL.' });
      } else {
        throw new Error('Save failed');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      setMessage({ type: 'error', text: '❌ Failed to save settings. Please try again.' });
    } finally {
      setSaving(false);
    }
  }

  if (isChecking) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/articles')}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Settings className="w-6 h-6" />
                  Settings
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Configure Naver TV video URL for new articles
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm p-16 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
            <p className="mt-6 text-lg font-medium text-gray-700">Loading settings...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Set the Naver TV video URL you want to use for new articles</li>
                    <li>• Choose the effective date (articles published on or after this date will use the new URL)</li>
                    <li>• Save the settings - new articles will automatically include this video</li>
                    <li>• You can update this anytime to change the video URL</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Settings Form */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Video className="w-5 h-5" />
                Naver TV Configuration
              </h2>

              <div className="space-y-6">
                {/* Naver TV URL */}
                <div>
                  <label htmlFor="naverTvUrl" className="block text-sm font-medium text-gray-700 mb-2">
                    Naver TV Video URL
                  </label>
                  <input
                    type="text"
                    id="naverTvUrl"
                    value={naverTvUrl}
                    onChange={(e) => setNaverTvUrl(e.target.value)}
                    placeholder="https://tv.naver.com/v/91011883"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Enter the full Naver TV video URL (e.g., https://tv.naver.com/v/91011883)
                  </p>
                </div>

                {/* Effective Date */}
                <div>
                  <label htmlFor="effectiveDate" className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    Effective Date
                  </label>
                  <input
                    type="date"
                    id="effectiveDate"
                    value={effectiveDate}
                    onChange={(e) => setEffectiveDate(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    Articles published on or after this date will use the new video URL
                  </p>
                </div>

                {/* Preview */}
                {naverTvUrl && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Preview</h3>
                    <div className="aspect-video bg-gray-200 rounded-lg overflow-hidden">
                      <iframe
                        src={naverTvUrl.replace('tv.naver.com/v/', 'tv.naver.com/embed/')}
                        frameBorder="0"
                        allowFullScreen
                        className="w-full h-full"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      This is how the video will appear in articles
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Message */}
            {message && (
              <div className={`rounded-lg p-4 flex items-start gap-3 ${
                message.type === 'success'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}>
                {message.type === 'success' ? (
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                )}
                <p className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                  {message.text}
                </p>
              </div>
            )}

            {/* Save Button */}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => router.push('/articles')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {saving ? (
                  <>
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Settings
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
