package org.doit.doitapp;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

import java.util.Map;

public final class DeadlineReminderScheduler {
    private static final String TAG = "DoItReminders";
    private static final String PREFS = "doit_deadline_reminders";
    private static final String CHANNEL_ID = "doit_deadlines";

    private DeadlineReminderScheduler() {}

    public static void schedule(
            Context context,
            int taskId,
            int offsetHours,
            long triggerAtMillis,
            String title,
            String message
    ) {
        String key = alarmKey(taskId, offsetHours);
        cancelReminder(context, key);

        SharedPreferences prefs = preferences(context);
        prefs.edit()
                .putLong(key + ".at", triggerAtMillis)
                .putString(key + ".title", title)
                .putString(key + ".message", message)
                .apply();
        setAlarm(context, key, triggerAtMillis, title, message);
    }

    public static void cancelTask(Context context, int taskId) {
        cancelReminder(context, alarmKey(taskId, 24));
        cancelReminder(context, alarmKey(taskId, 1));
    }

    public static void notifyNow(Context context, String title, String message) {
        showNotification(context, "new_" + System.currentTimeMillis(), title, message);
    }

    static void restoreAlarms(Context context) {
        Map<String, ?> entries = preferences(context).getAll();
        for (String key : entries.keySet()) {
            if (!key.startsWith("alarm_") || !key.endsWith(".at")) {
                continue;
            }
            String alarmKey = key.substring(0, key.length() - 3);
            long triggerAt = preferences(context).getLong(key, 0);
            String title = preferences(context).getString(alarmKey + ".title", "Pengingat Deadline DoIt");
            String message = preferences(context).getString(alarmKey + ".message", "Deadline tugas sudah dekat.");
            if (triggerAt > System.currentTimeMillis()) {
                setAlarm(context, alarmKey, triggerAt, title, message);
            } else {
                cancelReminder(context, alarmKey);
            }
        }
    }

    static void deliver(Context context, Intent intent) {
        String key = intent.getStringExtra("alarm_key");
        if (key == null || key.isEmpty()) {
            Log.e(TAG, "Alarm diterima tanpa identitas tugas");
            return;
        }
        showNotification(
                context,
                key,
                intent.getStringExtra("title"),
                intent.getStringExtra("message")
        );
        cancelReminder(context, key);
    }

    private static void setAlarm(Context context, String key, long at, String title, String message) {
        AlarmManager alarmManager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (alarmManager == null) {
            Log.e(TAG, "AlarmManager tidak tersedia");
            return;
        }

        Intent intent = reminderIntent(context, key, title, message);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pendingIntent);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pendingIntent);
        } else {
            alarmManager.setExact(AlarmManager.RTC_WAKEUP, at, pendingIntent);
        }
    }

    private static Intent reminderIntent(Context context, String key, String title, String message) {
        Intent intent = new Intent(context, DeadlineReminderReceiver.class);
        intent.setAction(context.getPackageName() + ".DEADLINE_REMINDER." + key);
        intent.setData(Uri.parse("doit://deadline/" + key));
        intent.putExtra("alarm_key", key);
        intent.putExtra("title", title);
        intent.putExtra("message", message);
        return intent;
    }

    private static void cancelReminder(Context context, String key) {
        AlarmManager alarmManager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(
                context,
                0,
                reminderIntent(context, key, "", ""),
                PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE
        );
        if (alarmManager != null && pendingIntent != null) {
            alarmManager.cancel(pendingIntent);
            pendingIntent.cancel();
        }
        preferences(context).edit()
                .remove(key + ".at")
                .remove(key + ".title")
                .remove(key + ".message")
                .apply();
    }

    private static String alarmKey(int taskId, int offsetHours) {
        return "alarm_" + taskId + "_" + offsetHours;
    }

    private static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static void showNotification(Context context, String key, String title, String message) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                && context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            Log.w(TAG, "Notifikasi belum diizinkan pengguna");
            return;
        }

        NotificationManager manager =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (manager == null) {
            Log.e(TAG, "NotificationManager tidak tersedia");
            return;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Pengingat Deadline",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Notifikasi tugas dan deadline dari DoIt");
            manager.createNotificationChannel(channel);
        }

        Intent launchIntent = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
        PendingIntent contentIntent = launchIntent == null ? null : PendingIntent.getActivity(
                context,
                key.hashCode(),
                launchIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        Notification.Builder builder = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? new Notification.Builder(context, CHANNEL_ID)
                : new Notification.Builder(context);
        builder.setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle(title == null ? "Pengingat Deadline DoIt" : title)
                .setContentText(message == null ? "Deadline tugas sudah dekat." : message)
                .setStyle(new Notification.BigTextStyle().bigText(
                        message == null ? "Deadline tugas sudah dekat." : message
                ))
                .setAutoCancel(true);
        if (contentIntent != null) {
            builder.setContentIntent(contentIntent);
        }
        manager.notify(key.hashCode(), builder.build());
    }
}
