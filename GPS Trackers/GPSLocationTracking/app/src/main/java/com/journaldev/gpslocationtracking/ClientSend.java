package com.journaldev.gpslocationtracking;

/**
 * Created by das_f on 16/05/2018.
 */

import android.annotation.SuppressLint;
import android.os.AsyncTask;
import android.os.Build;
import android.util.Log;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;

public class ClientSend {
    private AsyncTask<Void, Void, Void> async_cient;
    public String Message;

    public ClientSend() throws SocketException {
        ds = new DatagramSocket();
    }

    public String getIp() {
        return ip;
    }

    public void setIp(String ip) {
        this.ip = ip;
    }

    public String ip;

    public int getPort() {
        return port;
    }

    public void setPort(int port) {
        this.port = port;
    }

    public int port;
    public DatagramSocket ds;
    DatagramPacket dp;
    @SuppressLint({"NewApi", "StaticFieldLeak"})
    public void NachrichtSenden() {
        async_cient = new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(Void... params) {


                try {

                    dp = new DatagramPacket(Message.getBytes(), Message.length(), InetAddress.getByName(ip),port);
                    Log.d("Sending to:", ip + port +"");
                    ds.setBroadcast(true);
                    ds.send(dp);
                } catch (Exception e) {
                    e.printStackTrace();

                }
                return null;
            }

            protected void onPostExecute(Void result) {
                super.onPostExecute(result);
            }
        };

        if (Build.VERSION.SDK_INT >= 11)
            async_cient.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
        else async_cient.execute();
    }
}