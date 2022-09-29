package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.Camera;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.PersistableBundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialProber;
import com.hoho.android.usbserial.util.SerialInputOutputManager;
import com.lodong.android.eyetrackingtest.model.FireStorageInterface;
import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

import java.io.File;
import java.io.IOException;
import java.util.List;


//모듈 및 기기 정보를 담는 클래스
public class MainActivity extends AppCompatActivity {
    private static final String TAG = MainActivity.class.getSimpleName();
    private RadioGroup rdgDevice;
    private RadioButton rdbSmartPhone, rdbTablet;
    private TextView txtDeviceList;
    private LinearLayout linearNext;

    private final String DEVICE_TYPE_SMARTPHONE = "Smartphone";
    private final String DEVICE_TYPE_TABLET = "Tablet";
    private String userDeviceType = "";

    private int cameraCount;

    private FirebaseAuth mAuth;

    private final String USER = "user";
    private final String TEST_INFO = "test_info";
    private final String STORAGE = "storage";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        requestPermission();
        initView();
        setClickListener();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if(Environment.isExternalStorageManager()){
                getDeviceList();
                makeFolder();
            }else{
                try{
                    Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                    intent.addCategory("android.intent.category.DEFAULT");
                    intent.setData(Uri.parse(String.format("package:%s", getApplicationContext().getPackageName())));
                    startActivityForResult(intent, 1225);
                }catch (Exception e){
                    Intent intent = new Intent();
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    startActivityForResult(intent, 1225);
                }
            }
        }else{
            getDeviceList();
            makeFolder();
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        mAuth = FirebaseAuth.getInstance();
        /*login();*/
    }

    private void login() {
        mAuth.signInWithEmailAndPassword("android@gmail.com", "android99")
                .addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                    @Override
                    public void onComplete(@NonNull Task<AuthResult> task) {
                        if (task.isSuccessful()) {
                            // Sign in success, update UI with the signed-in user's information
                            Log.d(TAG, "createUserWithEmail:success");
                            FirebaseUser user = mAuth.getCurrentUser();
                        } else {
                            // If sign in fails, display a message to the user.
                            Log.w(TAG, "createUserWithEmail:failure", task.getException());
                        }
                    }
                });

    }

    private void requestPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {

            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED ||
                    ContextCompat.checkSelfPermission(this, Manifest.permission.MANAGE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED ||
                    ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO, Manifest.permission.MANAGE_EXTERNAL_STORAGE},
                        999);
            }
        }else{
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED ||
                    ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED ||
                    ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.RECORD_AUDIO},
                        999);
            }
        }
    }

    private void initView() {
        rdgDevice = findViewById(R.id.rdg_device);
        rdbSmartPhone = findViewById(R.id.rdb_smartphone);
        rdbTablet = findViewById(R.id.rdb_tablet);
        txtDeviceList = findViewById(R.id.txt_device_list);
        linearNext = findViewById(R.id.linear_next);
    }

    private void setClickListener() {
        rdgDevice.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i) {
                case R.id.rdb_smartphone:
                    userDeviceType = DEVICE_TYPE_SMARTPHONE;
                    break;
                case R.id.rdb_tablet:
                    userDeviceType = DEVICE_TYPE_TABLET;
                    break;
            }
        });

        linearNext.setOnClickListener(view -> {
            if (!userDeviceType.equals("")) {
                User user = User.getInstance();
                user.setDevice_type(userDeviceType);
                startActivity(new Intent(getApplicationContext(), LoginActivity.class));
            } else {
                Toast.makeText(getApplicationContext(), "옵션을 선택해주세요", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void getDeviceList() {
        StringBuilder connect_device_list = new StringBuilder();

        if (checkCameraHardware()) {
            connect_device_list.append("내장카메라(" + cameraCount + ") 대 사용 가능" + "\n");
        } else {
            connect_device_list.append("내장카메라 사용 불가능" + "\n");
        }

        if (!getGyroValue(connect_device_list)) {
            connect_device_list.append("연결된 디바이스 없음" + "\n");
        }

        displayDeviceList(connect_device_list);
    }

    private boolean checkCameraHardware() {
        if (getPackageManager().hasSystemFeature(PackageManager.FEATURE_CAMERA)) {
            // 카메라가 최소한 한개 있는 경우 처리
            cameraCount = Camera.getNumberOfCameras();
            Log.i(TAG, "Number of available camera : " + cameraCount);
            return true;
        } else {
            // 카메라가 전혀 없는 경우
            Toast.makeText(getApplicationContext(), "No camera found!", Toast.LENGTH_SHORT).show();
            return false;
        }

    }

    private boolean getGyroValue(StringBuilder connect_device_list) {
        UsbManager manager = (UsbManager) getSystemService(Context.USB_SERVICE);
        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(manager);
        if (availableDrivers.isEmpty()) {
            return false;
        }

        Log.d(TAG, "connected device count : " + availableDrivers.size());

        for (UsbSerialDriver usbSerialDriver : availableDrivers) {
            connect_device_list.append(usbSerialDriver.getDevice().getDeviceName() + "사용 가능" + "\n");
        }
        return true;
    }

    private void displayDeviceList(StringBuilder connect_device_list) {
        txtDeviceList.setText(connect_device_list);
    }

    private void makeFolder() {
        File dir = new File(Environment.getExternalStorageDirectory().getAbsolutePath() + "/HOME/" + "S1/");
        Log.d(TAG, "storage path" + dir.getAbsolutePath());

        Storage storage = Storage.getInstance();
        storage.setStorage(dir.getAbsolutePath()+"/");

        if (!dir.exists()) {
            dir.mkdirs();
            Log.d(TAG, "mkdir");
        } else {
            Log.d(TAG, "exist");
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == 1225){
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                if (Environment.isExternalStorageManager()) {
                    getDeviceList();
                    makeFolder();
                }else{
                    Toast.makeText(getApplicationContext(), "모든 파일에 대한 접근 권한 허용을 해주세요", Toast.LENGTH_SHORT).show();
                    finishAffinity();
                    System.exit(0);
                }
            }
        }
    }

    @Override
    public void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putSerializable(USER, User.getInstance());
        outState.putSerializable(TEST_INFO, TestInfo.getInstance());
        outState.putSerializable(STORAGE, Storage.getInstance());
    }

    @Override
    protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        User.setInstance((User) savedInstanceState.getSerializable(USER));
        TestInfo.setInstance((TestInfo) savedInstanceState.getSerializable(TEST_INFO));
        Storage.setInstance((Storage) savedInstanceState.getSerializable(STORAGE));
    }
}