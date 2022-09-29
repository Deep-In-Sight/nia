package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;

import android.content.Context;
import android.content.Intent;
import android.graphics.Point;
import android.graphics.drawable.ColorDrawable;
import android.hardware.Camera;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.icu.text.SimpleDateFormat;
import android.media.CamcorderProfile;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.util.Log;
import android.view.Display;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.auth.UserInfo;
import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialProber;
import com.hoho.android.usbserial.util.SerialInputOutputManager;
import com.lodong.android.eyetrackingtest.model.ScenarioData;
import com.lodong.android.eyetrackingtest.model.ScenarioModel;
import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;
import com.opencsv.CSVWriter;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.Date;
import java.util.List;
import java.util.RandomAccess;
import java.util.Timer;
import java.util.TimerTask;

//측정액티비티 - 자이로 센서값 기록 및 애니메이션 재생
public class MeasurementActivity extends AppCompatActivity implements SerialInputOutputManager.Listener, SurfaceHolder.Callback {
    private final String TAG = MeasurementActivity.class.getSimpleName();
    private int screenWidth;
    private int screenHeight;
    private int criWidth;
    private int criHeight;

    private ImageView circle;

    private float circleX;
    private float circleY;
    private int[] path;

    private Handler handler = new Handler();
    private Timer timer = new Timer();

    //시간 관련 변수
    private int tempTime;
    private float elapsedTime = 0;

    //카메라 관련 변수
    private SurfaceView mSurfaceView;
    private SurfaceHolder surfaceHolder;
    private Camera camera;
    private MediaRecorder mediaRecorder;

    //gyro 센서 관련 변수
    private SerialInputOutputManager usbIoManager;

    private boolean isRecord;
    private boolean recording;

    //파일 관련 변수
    private String videoName;
    private String txtName;
    private File saveFile;
    private RandomAccessFile raf;
    private String criRef;
    private String criGyroRef;
    private String criVideoRef;

    //display rotation
    int displayNum;
    int writenum;

   /* SimpleDateFormat sdf = new SimpleDateFormat("yyyy_MM_dd_hh_mm_ss");
    String nowTime;*/

    private final String USER = "user";
    private final String TEST_INFO = "test_info";
    private final String STORAGE = "storage";

    private CSVWriter csvWriter;

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
        setContentView(R.layout.activity_measurement);

        initView();
        settingScenario();
        showTimerDialog();
        //파일 세팅
        settingFileNames();

        //카메라 및 자이로 센서 준비
        settingGyroSensor();
    }

    private void initView() {
        circle = findViewById(R.id.img_circle);
        mSurfaceView = findViewById(R.id.surfaceView);
        surfaceHolder = mSurfaceView.getHolder();
        surfaceHolder.addCallback(MeasurementActivity.this);
        surfaceHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
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

    @Override
    protected void onResume() {
        super.onResume();

        int cameraId = findFrontSideCamera();
        camera = Camera.open(cameraId);
        camera.setDisplayOrientation(displayNum);
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            timer.cancel();
            usbIoManager.stop();
            raf.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        if (camera != null) {
            camera.release();
            camera = null;
        }
    }

    @Override
    public void onNewData(byte[] data) {
        //timer 동작 상태 확인 후 기록
        /*runOnUiThread(() -> { txtGyroValue.setText(new String(data)); });*/
        if (isRecord) {
            writeTxt(new String(data));
        }
    }

    @Override
    public void onRunError(Exception e) {
        e.printStackTrace();
    }

    private void settingFileNames() {
        User user = User.getInstance();
        String birth = user.getBirth();
        String name = user.getName();
        String sex = user.getSex();
        String device = user.getDevice_type();
        TestInfo testInfo = TestInfo.getInstance();
        int scenarioNum = testInfo.getLastSelectIndex();
        String scenarioString = String.valueOf(scenarioNum + 1);
        String posture = testInfo.getPostureString();
        String direction = testInfo.getDeviceDirectionString();
        String status = testInfo.getStatusString();
        String retry = String.valueOf(testInfo.getRetry());

        String subDIR2 = name + "/";
        String subDIR3 = "T"+retry + "/";
        String subDIR4 = device + "/";

        File dir = new File(Storage.getInstance().getStorage() + subDIR2 + subDIR3 + subDIR4);
        Log.d(TAG, "storage path" + dir.getAbsolutePath());

        criRef = dir.getAbsolutePath()+"/";

       /* Storage storage = Storage.getInstance();
        storage.setStorage(dir.getAbsolutePath()+"/");*/

        if (!dir.exists()) {
            dir.mkdirs();
            Log.d(TAG, "mkdir");
        } else {
            Log.d(TAG, "exist");
        }


        makeTxt(birth, name, scenarioString, device, status, posture, direction, retry);
    }

    private void settingGyroSensor() {
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

    private void makeTxt(String birth, String name, String scenarioNum, String device,
                         String status, String posture, String direction, String retry) {
        // csv 파일 생성
        String subDir5 = "GazeAngle1";
        String subject = "NIA22EYE";
        String location = "S1";
        String id = name;
        String uniqueNum = "T" + retry;
        Log.d(TAG, "scenarioNum : " + scenarioNum);
        String scenario = "S"+String.format("%02d", Integer.parseInt(scenarioNum));
        String display = device.equals("SmartPhone") ? "S": "T";
        String dataType = "gaze1";
        String statusPath= "";
        String posturePath = "";
        String directionPath = "";

        int statusNum = TestInfo.getInstance().getStatus();
        switch (statusNum){
            case 0 :
                statusPath = "F";
                break;
            case 1:
                statusPath = "S";
                break;
            case 2:
                statusPath = "D";
                break;
            case 3:
                statusPath = "A";
                break;
            case 4:
                statusPath = "N";
                break;
        }

        int postureNum = TestInfo.getInstance().getPosture();

        switch (postureNum){
            case 0:
                posturePath = "S";
                break;
            case 1:
                posturePath = "D";
                break;
            case 2:
                posturePath = "H";
                break;
            case 3:
                posturePath = "E";
                break;
            case 4:
                posturePath = "K";
                break;
            case 5:
                posturePath = "U";
                break;
            case 6:
                posturePath = "C";
                break;
            case 7:
                posturePath = "P";
                break;
            case 8:
                posturePath = "L";
                break;
            case 9:
                posturePath = "F";
                break;

        }

        int directionNum = TestInfo.getInstance().getDeviceDirection();
        switch (directionNum){
            case 0 :
                directionPath = "L";
                break;
            case 1:
                directionPath = "T";
                break;
            case 2:
                directionPath = "R";
                break;
        }

        String fileName = subject + "_" + location + "_" + id + "_"
                + uniqueNum + "_" + scenario + "_" + display + "_"
                + dataType + "_" + statusPath + "_" + posturePath + "_" + directionPath+".csv";

        File dir = new File(criRef + "/" + subDir5);
        Log.d(TAG, "gyro1storage path" + dir.getAbsolutePath());
        Log.d(TAG, "gyro1FileName : "+fileName);
        this.txtName = fileName;
        criGyroRef = dir.getAbsolutePath()+"/";

        if (!dir.exists()) {
            dir.mkdirs();
            Log.d(TAG, "mkdir");
        } else {
            Log.d(TAG, "exist");
        }

        try {
            csvWriter = new CSVWriter(new FileWriter(criGyroRef + fileName));
        } catch (IOException e) {
            e.printStackTrace();
        }

       /* File saveFile = new File( criRef + txtName);
        try {
            saveFile.createNewFile();
            this.saveFile = saveFile;
            this.raf = new RandomAccessFile(saveFile, "rw");
            *//*Storage.getInstance().setLastSaveTxt(Storage.getInstance().getStorage() +"/"+ txtName);*//*
            Toast.makeText(this, "create Success", Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            e.printStackTrace();
        }*/
        makeVideoFoleder(birth, name, scenarioNum, device, status, posture, direction, retry);
    }

    private void makeVideoFoleder(String birth, String name, String scenarioNum, String device,
                                  String status, String posture, String direction, String retry){
        String subDir5 = "RGB";
        String subject = "NIA22EYE";
        String location = "S1";
        String id = name;
        String uniqueNum = "T" + retry;
        String scenario = "S"+String.format("%02d", Integer.parseInt(scenarioNum));
        String display = device.equals("SmartPhone") ? "S": "T";
        String dataType = "rgb";
        String statusPath= "";
        String posturePath = "";
        String directionPath = "";

        int statusNum = TestInfo.getInstance().getStatus();
        switch (statusNum){
            case 0 :
                statusPath = "F";
                break;
            case 1:
                statusPath = "S";
                break;
            case 2:
                statusPath = "D";
                break;
            case 3:
                statusPath = "A";
                break;
            case 4:
                statusPath = "N";
                break;
        }

        int postureNum = TestInfo.getInstance().getPosture();

        switch (postureNum){
            case 0:
                posturePath = "S";
                break;
            case 1:
                posturePath = "D";
                break;
            case 2:
                posturePath = "H";
                break;
            case 3:
                posturePath = "E";
                break;
            case 4:
                posturePath = "S";
                break;
            case 5:
                posturePath = "U";
                break;
            case 6:
                posturePath = "C";
                break;
            case 7:
                posturePath = "P";
                break;
            case 8:
                posturePath = "L";
                break;
            case 9:
                posturePath = "F";
                break;
        }

        int directionNum = TestInfo.getInstance().getDeviceDirection();
        switch (directionNum){
            case 0 :
                directionPath = "L";
                break;
            case 1:
                directionPath = "T";
                break;
            case 2:
                directionPath = "R";
                break;
        }


        String fileName = subject + "_" + location + "_" + id + "_"
                + uniqueNum + "_" + scenario + "_" + display + "_"
                + dataType + "_" + statusPath + "_" + posturePath + "_"+directionPath+ ".mp4";


        File dir = new File(criRef + "/" + subDir5);
        Log.d(TAG, "rgbstorage path" + dir.getAbsolutePath());
        Log.d(TAG, "rgbFileName : "+fileName);

        criVideoRef = dir.getAbsolutePath()+"/";

        if (!dir.exists()) {
            dir.mkdirs();
            Log.d(TAG, "mkdir");
        } else {
            Log.d(TAG, "exist");
        }

        this.videoName = fileName;
    }


    private void record() {
        runOnUiThread(() -> {
            try {
                mediaRecorder = new MediaRecorder();
                camera.unlock();
                mediaRecorder.setCamera(camera);
                mediaRecorder.setAudioSource(MediaRecorder.AudioSource.CAMCORDER);
                mediaRecorder.setVideoSource(MediaRecorder.VideoSource.CAMERA);
                mediaRecorder.setProfile(CamcorderProfile.get(CamcorderProfile.QUALITY_1080P));
                mediaRecorder.setOrientationHint(writenum);
                mediaRecorder.setOutputFile(criVideoRef + videoName);
                /*Storage.getInstance().setLastSaveVideo(Storage.getInstance().getStorage() + videoName);*/
                Log.d(TAG, criRef + videoName);
                mediaRecorder.setPreviewDisplay(surfaceHolder.getSurface());
                mediaRecorder.prepare();
                mediaRecorder.start();
                recording = true;
                startTimer();
            } catch (IOException e) {
                Toast.makeText(getApplicationContext(), "영상 녹화 실패", Toast.LENGTH_SHORT).show();
                e.printStackTrace();
                mediaRecorder.release();
            }
        });

    }

    private void writeTxt(String value) {
        /*try {
            this.raf.seek(this.raf.length());
            this.raf.writeBytes(value + "\n");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }*/
        String[] entries = {value};
        csvWriter.writeNext(entries);
    }

    private void stopWriteTxt() {
        try {
            csvWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void stopRecord() {
        Log.d(TAG, "stopRecord");
        try {
            mediaRecorder.stop();
            mediaRecorder.release();
            camera.lock();
            recording = false;
        } catch (IllegalStateException e) {
            e.printStackTrace();
        }
    }

    private void settingScenario() {
        //Get Screen Size
        WindowManager wm = getWindowManager();
        Display disp = wm.getDefaultDisplay();
        Point size = new Point();
        disp.getSize(size);
        screenWidth = size.x;
        screenHeight = size.y;
        this.criWidth = screenWidth - (screenWidth / 10);
        this.criHeight = screenHeight - (screenHeight / 10);

        getScenarioData();
    }

    private void getScenarioData() {
        TestInfo testInfo = TestInfo.getInstance();
        int scenaioNum = testInfo.getScenarioNum();
        int status = testInfo.getStatus();
        Log.d(TAG, "scenaioNum : " + scenaioNum);
        Log.d(TAG, "status : " + status);
        ScenarioModel scenarioModel = new ScenarioModel(status, scenaioNum, MeasurementActivity.this);

        int[] path = scenarioModel.getPath();
        float startX = scenarioModel.getStartX();
        float startY = scenarioModel.getStartY();

        this.path = path;
        settingCircle(startX, startY);
    }

    private void settingCircle(float startX, float startY) {
        ConstraintLayout.LayoutParams cp = (ConstraintLayout.LayoutParams) circle.getLayoutParams();
        cp.width = screenWidth / 10;
        cp.height = screenHeight / 10;
        circle.setLayoutParams(cp);
        circleX = startX;
        circleY = startY;
        //initial X, Y
        circle.setX(circleX);
        circle.setY(circleY);
        Log.d(TAG, "startX : " + circleX);
        Log.d(TAG, "startY : " + circleY);
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

    private void startScenario() {
        elapsedTime = 0;
       /* TestInfo.getInstance().setTestTime(getTime());*/
        record();
    }

    private void startTimer() {
        //Start the timer
        isRecord = true;
        Log.d(TAG, "starterTimer");
        try {
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    handler.post(() -> {
                        if (elapsedTime > 9.999f) {
                            isRecord = false;
                            stopRecord();
                            stopWriteTxt();
                            Log.d(TAG, "animation end");
                            Log.d(TAG, String.valueOf(elapsedTime));
                            intentResultActivity();
                            timer.cancel();
                            if (handler != null) {
                                handler.removeMessages(0);
                            }
                    } else {
                            int index = (int) elapsedTime;
                            changePos(path[index]);
                            elapsedTime += 1.0f / 100.0f;
                        }
                    });
                }
            }, 0, 10);
        } catch (IllegalStateException e) {
            e.printStackTrace();
        }
    }


    private void changePos(int direction) {
        if (direction == 0) {
            // Up
            circleY -= criHeight / 1000.0f;
            if (circle.getY() + circle.getHeight() < 0) {
                circleX = (float) Math.floor(Math.random() * (screenWidth - circle.getWidth()));
                circleY = screenHeight + 100.f;
            }
            circle.setX(circleX);
            circle.setY(circleY);

        } else if (direction == 1) {
            // Down
            circleY += criHeight / 1000.0f;
            if (circle.getY() > screenHeight) {
                circleX = (float) Math.floor(Math.random() * (screenWidth - circle.getWidth()));
                circleY = -100.f;
            }
            circle.setX(circleX);
            circle.setY(circleY);

        } else if (direction == 2) {
            // Left
            circleX -= criWidth / 1000.0f;
            if (circle.getX() + circle.getWidth() < 0) {
                circleX = criWidth + 100.0f;
                circleY = (float) Math.floor(Math.random() * (screenHeight - circle.getHeight()));
            }
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 3) {
            // Right
            circleX += criWidth / 1000.0f;
            if (circle.getX() > screenWidth) {
                circleX = -100.0f;
                circleY = (float) Math.floor(Math.random() * (screenHeight - circle.getHeight()));
            }
            Log.d(TAG, String.valueOf(circleX));
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 4) {
            // 왼쪽 위 대각선 방향
            circleX -= criWidth / 1000.0f;
            circleY -= criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 5) {
            // 왼쪽 아래 대각선 방향
            circleX -= criWidth / 1000.0f;
            circleY += criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 6) {
            // 오른쪽 위 대각선 방향
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 7) {
            // 오른쪽 아래 대각선 방향
            circleX += criWidth / 1000.0f;
            circleY += criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 8) {
            //left down direction - half Y
            circleX -= criWidth / 500.0f;
            circleY += criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 9) {
            //left down direction - half X
            circleX -= criWidth / 2000.0f;
            circleY += criHeight / 500.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 10) {
            //right down direction - half Y
            circleX += criWidth / 500.0f;
            circleY += criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 11) {
            //right down direction - half X
            circleX += criWidth / 1000.0f;
            circleY += criHeight / 500.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 12) {
            //stop
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 13) {
            //left up direction - half Y
            circleX -= criWidth / 1000.0f;
            circleY -= criHeight / 2000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 14) {
            //left up direction - half X
            circleX -= criWidth / 2000.0f;
            circleY -= criHeight / 1000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 15) {
            //right up direction - half Y
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 2000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 16) {
            //right up direction - half X
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 500.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 17) {
            circleX += criWidth / 800.0f;
            circleY += criHeight / 3000.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 18) {
            //right up direction - half Y
            circleX += criWidth / 500.0f;
            circleY -= criHeight / 900.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 19) {
            //right down direction - half X
            circleX += criWidth / 2000.0f;
            circleY += criHeight / 500.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 20) {
            circleX += criWidth / 1000.0f;
            circleY += criHeight / 300.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 21) {
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 300.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 22) {
            circleX += criWidth / 1000.0f;
            circleY += criHeight / 400.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 23) {
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 300.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 24) {
            circleX += criWidth / 1000.0f;
            circleY += criHeight / 300.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        } else if (direction == 25) {
            circleX += criWidth / 1000.0f;
            circleY -= criHeight / 400.0f;
            circle.setX(circleX);
            circle.setY(circleY);
        }
    }

    private void showTimerDialog() {
        View dialogView = getLayoutInflater().inflate(R.layout.dialog_timer, null);

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setView(dialogView);

        final AlertDialog alertDialog = builder.create();
        alertDialog.getWindow().setBackgroundDrawable(new ColorDrawable(android.graphics.Color.TRANSPARENT));
        alertDialog.show();

        Timer timerCall;
        timerCall = new Timer();
        TextView txtTimer = dialogView.findViewById(R.id.txt_time);

        int time = 4;
        tempTime = 0;
        TimerTask timerTask = new TimerTask() {
            @Override
            public void run() {
                runOnUiThread(() -> txtTimer.setText(String.valueOf(time - tempTime)));
                tempTime++;
                Log.d(TAG, "tempTime : " + tempTime);
                if (tempTime == 4) {
                    alertDialog.dismiss();
                    startScenario();
                    timerCall.cancel();
                }
            }
        };
        timerCall.schedule(timerTask, 0, 1000);
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
    public void surfaceChanged(@NonNull SurfaceHolder surfaceHolder, int i, int i1, int i2) {
        refreshCamera(camera);
    }

    @Override
    public void surfaceDestroyed(@NonNull SurfaceHolder surfaceHolder) {

    }

    private void intentResultActivity() {
        Log.d(TAG, "intentResultActivity");
        startActivity(new Intent(getApplicationContext(), ResultActivity.class));
        finish();
    }

   /* private String getTime(){
        long mNow = System.currentTimeMillis();
        Date mDate = new Date(mNow);
        return sdf.format(mDate);
    }*/
}