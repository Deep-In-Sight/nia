package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;

import android.content.Intent;
import android.hardware.Camera;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.media.CamcorderProfile;
import android.media.ExifInterface;

import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.util.SparseIntArray;

import android.view.Display;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialProber;
import com.hoho.android.usbserial.util.SerialInputOutputManager;
import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

import java.io.IOException;

import java.util.List;

//테스트전 모듈 상태 확인용 액티비티
public class CheckDeviceActivity extends AppCompatActivity implements SerialInputOutputManager.Listener, SurfaceHolder.Callback {
    private final String TAG = CheckDeviceActivity.class.getSimpleName();
    private TextView txtGyroValue;
    private Button btn_record;
    private SerialInputOutputManager usbIoManager;

    private SurfaceView mSurfaceView;

    private Camera camera;
    private MediaRecorder mediaRecorder;
    private SurfaceHolder surfaceHolder;
    private boolean recording = false;

    private TextView txtBack;
    private ImageView imgBack;
    private LinearLayout linearNext;

    int displayNum;
    int writenum;
    private static final SparseIntArray ORIENTATION = new SparseIntArray();

    static {
        ORIENTATION.append(ExifInterface.ORIENTATION_NORMAL, 0);
        ORIENTATION.append(ExifInterface.ORIENTATION_ROTATE_90, 90);
        ORIENTATION.append(ExifInterface.ORIENTATION_ROTATE_180, 180);
        ORIENTATION.append(ExifInterface.ORIENTATION_ROTATE_270, 270);
    }

    private final String USER = "user";
    private final String TEST_INFO = "test_info";
    private final String STORAGE = "storage";

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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_check_device);

        initView();
        setOnClickListener();
    }

    private void initView() {
        txtGyroValue = findViewById(R.id.txt_gyro_value);

        mSurfaceView = findViewById(R.id.surfaceView);
        surfaceHolder = mSurfaceView.getHolder();
        surfaceHolder.addCallback(CheckDeviceActivity.this);
        surfaceHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
        btn_record = findViewById(R.id.btn_record);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
        linearNext = findViewById(R.id.linear_start);

        Display display = getWindowManager().getDefaultDisplay();
        float newRotation = 0.0f;
        switch (display.getRotation()) {
            case Surface.ROTATION_0:        // 스마트폰 세로
                displayNum = 90;
                writenum = 270;
                break;
            case Surface.ROTATION_90:        // 스마트폰 왼쪽으로 누음
                displayNum = 0;
                writenum = 0;
                break;
            case Surface.ROTATION_180:        // 스마트폰은 보통 거꾸로를 지원하지 않는다. 따라서 스마트폰은 여기에 오지를 않는다.
                displayNum = 270;
                writenum = 90;
                break;
            case Surface.ROTATION_270:        // 스마트폰 오른쪽으로 누음
                displayNum = 180;
                writenum = 180;
                break;
        }
    }

    private void setOnClickListener() {
        btn_record.setOnClickListener(view -> recording());
        linearNext.setOnClickListener(view -> startActivity(new Intent(getApplicationContext(), MeasurementActivity.class)));

        imgBack.setOnClickListener(view -> onBackPressed());
        txtBack.setOnClickListener(view -> onBackPressed());
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (camera != null) {
            camera.stopPreview();
            camera.release();
            camera = null;
        }
        try {
            usbIoManager.stop();
        } catch (NullPointerException e) {

        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        int cameraId = findFrontSideCamera();
        camera = Camera.open(cameraId);
        camera.setDisplayOrientation(displayNum);
        getGyroValue();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }

    @Override
    public void onNewData(byte[] data) {
        runOnUiThread(() -> {
            txtGyroValue.setText(new String(data));
        });
    }

    @Override
    public void onRunError(Exception e) {
        e.printStackTrace();
    }

    @Override
    public void surfaceCreated(@NonNull SurfaceHolder surfaceHolder) {
        if (surfaceHolder.getSurface() == null) {
            return;
        }
        try {
            camera.stopPreview();
        } catch (Exception e) {
            e.printStackTrace();
        }
        setCamera(camera);
    }

    @Override
    public void surfaceChanged(@NonNull SurfaceHolder holder, int format, int width, int height) {
        refreshCamera(camera);
    }

    @Override
    public void surfaceDestroyed(@NonNull SurfaceHolder holder) {

    }

    private void getGyroValue() {
        UsbManager manager = (UsbManager) getSystemService(Context.USB_SERVICE);
        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(manager);
        if (availableDrivers.isEmpty()) {
            return;
        }

        UsbSerialDriver driver = availableDrivers.get(0);
        UsbDeviceConnection connection = manager.openDevice(driver.getDevice());
        if (connection == null) {
            return;
        }

        UsbSerialPort port = driver.getPorts().get(0);
        try {
            port.open(connection);
            port.setParameters(921600, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE);
        } catch (IOException e) {
            e.printStackTrace();
        }

        usbIoManager = new SerialInputOutputManager(port, this);
        usbIoManager.start();
    }

    private void recording() {
        if (recording) {
            mediaRecorder.stop();
            mediaRecorder.release();
            camera.lock();
            recording = false;
        } else {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        initView();
                        mediaRecorder = new MediaRecorder();
                        camera.unlock();
                        mediaRecorder.setCamera(camera);
                        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.CAMCORDER);
                        mediaRecorder.setVideoSource(MediaRecorder.VideoSource.CAMERA);
                        mediaRecorder.setProfile(CamcorderProfile.get(CamcorderProfile.QUALITY_1080P));
                        mediaRecorder.setOrientationHint(writenum);
                        Log.d(TAG, String.valueOf(Environment.getExternalStorageDirectory()));
                        mediaRecorder.setOutputFile(Storage.getInstance().getStorage() + "/test.mp4");
                        mediaRecorder.setPreviewDisplay(surfaceHolder.getSurface());
                        mediaRecorder.prepare();
                        mediaRecorder.start();
                        recording = true;
                    } catch (IOException e) {
                        Toast.makeText(getApplicationContext(), "영상 녹화 실패", Toast.LENGTH_SHORT).show();
                        e.printStackTrace();
                        mediaRecorder.release();
                    }
                }
            });
        }
    }

    private void setCamera(Camera cam) {
        camera = cam;
    }

    private void refreshCamera(Camera camera) {
        if (surfaceHolder.getSurface() == null) {
            return;
        }
        try {
            camera.stopPreview();
        } catch (Exception e) {
            e.printStackTrace();
        }
        setCamera(camera);
    }

    private int findFrontSideCamera() {
        int cameraId = -1;
        int numberOfCameras = Camera.getNumberOfCameras();

        for (int i = 0; i < numberOfCameras; i++) {
            Camera.CameraInfo cmInfo = new Camera.CameraInfo();
            Camera.getCameraInfo(i, cmInfo);

            if (cmInfo.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
                cameraId = i;
                break;
            }
        }

        return cameraId;
    }
}

