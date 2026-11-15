package com.hussain.jarvis;

import android.app.PendingIntent;
import android.content.Intent;
import android.os.Build;
import android.service.quicksettings.Tile;
import android.service.quicksettings.TileService;

/** Part 38: a Quick Settings tile. One tap opens Jarvis and starts listening. It never listens by itself and never works while Jarvis is stopped or locked. */
public class JarvisTile extends TileService {
    @Override public void onStartListening() {
        Tile t = getQsTile();
        if (t == null) return;
        t.setState(Privacy.stopped ? Tile.STATE_UNAVAILABLE : Tile.STATE_INACTIVE);
        t.setLabel("Jarvis");
        t.updateTile();
    }

    @Override public void onClick() {
        Intent i = new Intent(this, MainActivity.class).setAction(MainActivity.LISTEN).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        if (Build.VERSION.SDK_INT >= 34) startActivityAndCollapse(PendingIntent.getActivity(this, 0, i, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT));
        else startActivityAndCollapse(i);
    }
}
