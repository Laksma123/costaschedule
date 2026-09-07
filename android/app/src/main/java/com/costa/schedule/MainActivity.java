package com.costa.schedule;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.AlarmClock;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url != null && url.startsWith("intent:")) {
                    try {
                        Intent intent = Intent.parseUri(url, Intent.URI_INTENT_SCHEME);
                        if (intent != null) {
                            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                            startActivity(intent);
                            return true;
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(MainActivity.this, "Cannot open Clock app: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                    return true;
                }
                return false;
            }
        });
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new WebAppInterface(this), "AndroidBridge");
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    public class WebAppInterface {
        Context mContext;

        WebAppInterface(Context c) {
            mContext = c;
        }

        @JavascriptInterface
        public boolean isAndroidApp() {
            return true;
        }

        @JavascriptInterface
        public void showToast(String message) {
            mainHandler.post(() -> Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface
        public void setAlarm(int hour, int minute, String message) {
            setAlarm(hour, minute, message, false);
        }

        @JavascriptInterface
        public void setAlarm(int hour, int minute, String message, boolean skipUi) {
            mainHandler.post(() -> {
                try {
                    triggerAlarmIntent(hour, minute, message, skipUi);
                    String timeStr = String.format("%02d:%02d", hour, minute);
                    Toast.makeText(mContext, "⏰ Opening Clock for alarm " + timeStr, Toast.LENGTH_SHORT).show();
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(mContext, "Failed to set alarm: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void setThreeAlarms(int h1, int m1, int h2, int m2, int h3, int m3, String title) {
            mainHandler.post(() -> {
                try {
                    String timeStr1 = String.format("%02d:%02d", h1, m1);
                    String timeStr2 = String.format("%02d:%02d", h2, m2);
                    String timeStr3 = String.format("%02d:%02d", h3, m3);

                    // 1st alarm (with UI so user sees and confirms the alarm)
                    triggerAlarmIntent(h1, m1, title + " (Alarm 1 - " + timeStr1 + ")", false);

                    Toast.makeText(mContext, "⏰ 1st Alarm: " + timeStr1 + " (Copied: " + timeStr2 + ", " + timeStr3 + ")", Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(mContext, "Error setting alarms: " + e.getMessage(), Toast.LENGTH_LONG).show();
                }
            });
        }

        private void triggerAlarmIntent(int hour, int minute, String message, boolean skipUi) {
            try {
                Intent intent = new Intent(AlarmClock.ACTION_SET_ALARM);
                intent.putExtra(AlarmClock.EXTRA_HOUR, hour);
                intent.putExtra(AlarmClock.EXTRA_MINUTES, minute);
                intent.putExtra(AlarmClock.EXTRA_MESSAGE, message);
                intent.putExtra(AlarmClock.EXTRA_SKIP_UI, skipUi);
                intent.putExtra(AlarmClock.EXTRA_VIBRATE, true);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                mContext.startActivity(intent);
            } catch (Exception e) {
                e.printStackTrace();
                mainHandler.post(() -> Toast.makeText(mContext, "Failed to open Clock: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
        }
    }
}

