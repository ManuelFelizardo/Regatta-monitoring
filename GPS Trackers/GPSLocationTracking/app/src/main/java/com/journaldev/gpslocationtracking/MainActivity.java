package com.journaldev.gpslocationtracking;

import android.annotation.TargetApi;
import android.content.Context;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static android.Manifest.permission.ACCESS_COARSE_LOCATION;
import static android.Manifest.permission.ACCESS_FINE_LOCATION;

public class MainActivity extends AppCompatActivity implements SensorEventListener {


    private ArrayList<String> permissionsToRequest;
    private ArrayList<String> permissionsRejected = new ArrayList<>();
    private ArrayList<String> permissions = new ArrayList<>();
    private SensorManager sensorManager;
    private Sensor compass;
    private float compDegree;

    private final static int ALL_PERMISSIONS_RESULT = 101;
    LocationTrack locationTrack;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        compDegree = 0;
        permissions.add(ACCESS_FINE_LOCATION);
        permissions.add(ACCESS_COARSE_LOCATION);

        permissionsToRequest = findUnAskedPermissions(permissions);
        //get the permissions we have asked for before but are not granted..
        //we will store this in a global list to access later.


        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {


            if (permissionsToRequest.size() > 0)
                requestPermissions(permissionsToRequest.toArray(new String[permissionsToRequest.size()]), ALL_PERMISSIONS_RESULT);
        }


        Button btn = (Button) findViewById(R.id.btn);
        final TextView longit = (TextView) findViewById(R.id.textLong);
        final TextView latit = (TextView) findViewById(R.id.textLat);
        final EditText ip = (EditText) findViewById(R.id.editIp);
        final EditText port = (EditText) findViewById(R.id.editPort);
        final EditText type = (EditText) findViewById(R.id.editType);
        final TextView comp = (TextView) findViewById(R.id.textComp);
        final EditText id = (EditText) findViewById(R.id.editID);
        locationTrack = new LocationTrack(MainActivity.this);




        sensorManager = (SensorManager)getSystemService(Context.SENSOR_SERVICE);
        compass = sensorManager.getDefaultSensor(Sensor.TYPE_ORIENTATION);
        if(compass != null){
            sensorManager.registerListener(this, compass, SensorManager.SENSOR_DELAY_NORMAL);
        }






        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                final ClientSend clientSend;
                try {
                    clientSend = new ClientSend();
                    final Handler handler = new Handler();
                    final String ipText, portText, typeText, idText;

                    idText = id.getText().toString();
                    ipText = ip.getText().toString();
                    portText = port.getText().toString();
                    typeText = type.getText().toString();
                    clientSend.setIp(ipText);
                    clientSend.setPort(Integer.parseInt(portText));
                    handler.postDelayed(new Runnable() {
                        public void run() {
                            if (locationTrack.canGetLocation()) {
                                double longitude = locationTrack.getLongitude();
                                double latitude = locationTrack.getLatitude();
                                longit.setText(longitude+"");
                                latit.setText(latitude+"");
                                JSONObject object =  new JSONObject();
                                comp.setText(compDegree+"");
                                try {
                                    object.put("deviceId" , getMacAddr());
                                    object.put("type",typeText);
                                    object.put("Lat" , latitude);
                                    object.put("Long" , longitude);
                                    object.put("degree", compDegree);
                                    object.put("id", idText);
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                                Log.d("json", object.toString());
                                clientSend.Message = object.toString();
                                clientSend.NachrichtSenden();
                                //Toast.makeText(getApplicationContext(), "Longitude:" + Double.toString(longitude) + "\nLatitude:" + Double.toString(latitude), Toast.LENGTH_SHORT).show();
                            } else {
                                locationTrack.showSettingsAlert();
                            }
                            handler.postDelayed(this, 2000);
                        }
                    }, 3000);
                } catch (SocketException e) {
                    e.printStackTrace();
                }

            }
        });
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        this.compDegree  = Math.round(event.values[0]);
    }
    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }


    public static String getMacAddr() {
        try {
            List<NetworkInterface> all = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface nif : all) {
                if (!nif.getName().equalsIgnoreCase("wlan0")) continue;

                byte[] macBytes = nif.getHardwareAddress();
                if (macBytes == null) {
                    return "";
                }

                StringBuilder res1 = new StringBuilder();
                for (byte b : macBytes) {
                    res1.append(String.format("%02X:",b));
                }

                if (res1.length() > 0) {
                    res1.deleteCharAt(res1.length() - 1);
                }
                return res1.toString();
            }
        } catch (Exception ex) {
        }
        return "02:00:00:00:00:00";
    }

    private ArrayList<String> findUnAskedPermissions(ArrayList<String> wanted) {
        ArrayList<String> result = new ArrayList<String>();

        for (String perm : wanted) {
            if (!hasPermission(perm)) {
                result.add(perm);
            }
        }

        return result;
    }

    private boolean hasPermission(String permission) {
        if (canMakeSmores()) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                return (checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED);
            }
        }
        return true;
    }

    private boolean canMakeSmores() {
        return (Build.VERSION.SDK_INT > Build.VERSION_CODES.LOLLIPOP_MR1);
    }


    @TargetApi(Build.VERSION_CODES.M)
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {

        switch (requestCode) {

            case ALL_PERMISSIONS_RESULT:
                for (String perms : permissionsToRequest) {
                    if (!hasPermission(perms)) {
                        permissionsRejected.add(perms);
                    }
                }

                if (permissionsRejected.size() > 0) {


                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        if (shouldShowRequestPermissionRationale(permissionsRejected.get(0))) {
                            showMessageOKCancel("These permissions are mandatory for the application. Please allow access.",
                                    new DialogInterface.OnClickListener() {
                                        @Override
                                        public void onClick(DialogInterface dialog, int which) {
                                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                                requestPermissions(permissionsRejected.toArray(new String[permissionsRejected.size()]), ALL_PERMISSIONS_RESULT);
                                            }
                                        }
                                    });
                            return;
                        }
                    }

                }

                break;
        }

    }

    private void showMessageOKCancel(String message, DialogInterface.OnClickListener okListener) {
        new AlertDialog.Builder(MainActivity.this)
                .setMessage(message)
                .setPositiveButton("OK", okListener)
                .setNegativeButton("Cancel", null)
                .create()
                .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        locationTrack.stopListener();
    }
}
