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

        webView.setWebViewClient(new WebViewClient());
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
        public void setAlarm(int hour, int minute, String message, boolean skipUi) {
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
                mainHandler.post(() -> Toast.makeText(mContext, "Unable to set alarm: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
        }

        @JavascriptInterface
        public void setThreeAlarms(int h1, int m1, int h2, int m2, int h3, int m3, String title) {
            mainHandler.post(() -> {
                try {
                    String timeStr1 = String.format("%02d:%02d", h1, m1);
                    String timeStr2 = String.format("%02d:%02d", h2, m2);
                    String timeStr3 = String.format("%02d:%02d", h3, m3);

                    // 1st alarm
                    triggerAlarmIntent(h1, m1, title + " (Alarm 1 - " + timeStr1 + ")", true);

                    // 2nd alarm after 200ms delay to ensure system registers separate intent
                    mainHandler.postDelayed(() -> {
                        triggerAlarmIntent(h2, m2, title + " (Alarm 2 - " + timeStr2 + ")", true);
                    }, 250);

                    // 3rd alarm after 500ms delay
                    mainHandler.postDelayed(() -> {
                        triggerAlarmIntent(h3, m3, title + " (Alarm 3 - " + timeStr3 + ")", true);
                    }, 500);

                    Toast.makeText(mContext, "⏰ 3 Alarms set: " + timeStr1 + ", " + timeStr2 + ", " + timeStr3, Toast.LENGTH_LONG).show();
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
            }
        }
    }
}

