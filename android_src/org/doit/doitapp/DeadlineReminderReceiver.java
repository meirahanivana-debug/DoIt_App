package org.doit.doitapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public final class DeadlineReminderReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        DeadlineReminderScheduler.deliver(context, intent);
    }
}
