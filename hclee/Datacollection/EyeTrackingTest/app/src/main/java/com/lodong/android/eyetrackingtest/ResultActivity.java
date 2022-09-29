package com.lodong.android.eyetrackingtest;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.Observer;

import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;
import com.lodong.android.eyetrackingtest.model.FireStorageInterface;
import com.lodong.android.eyetrackingtest.model.RealTimeDatabaseInterface;
import com.lodong.android.eyetrackingtest.model.SaveData;
import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;

//결과 화면 출력 액티비티
public class ResultActivity extends AppCompatActivity {
    private static final String TAG = ResultActivity.class.getSimpleName() ;
    private FireStorageInterface fireStorageInterface;
    private RealTimeDatabaseInterface realTimeDatabaseInterface;
    private ProgressDialog asyncVideoDialog;
    private ProgressDialog asyncTxtDialog;
    private ProgressDialog asyncSaveVideoDialog;
    private ProgressDialog asyncSaveTxtDialog;
    private Button btnReStart;
    private LinearLayout btnChangeStatus, btnChangeDeviceDirection, btnChangeUserPosture, btnChangeDevice, linearExit, linearScenario;
    private TextView txtChangeStatus, txtChangeDeviceDirection, txtChangeUserPosture, txtChangeDevice, txtExit, txtScenario;
    private String videoUrl;
    private String txtUrl;

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
        setContentView(R.layout.activity_result);
        initView();
        setOnClickListener();
//        settingDatabase();
    }

    private void initView(){
        asyncVideoDialog = new ProgressDialog(ResultActivity.this);
        asyncVideoDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        asyncVideoDialog.setMessage("서버로 파일을 전송중입니다.");
        asyncTxtDialog = new ProgressDialog(ResultActivity.this);
        asyncTxtDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        asyncTxtDialog.setMessage("서버로 파일을 전송중입니다.");
        asyncSaveTxtDialog = new ProgressDialog(ResultActivity.this);
        asyncSaveTxtDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        asyncSaveTxtDialog.setMessage("파일 경로를 저장중입니다.");
        asyncSaveVideoDialog = new ProgressDialog(ResultActivity.this);
        asyncSaveVideoDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        asyncSaveVideoDialog.setMessage("파일 경로를 저장중입니다.");

        btnReStart = findViewById(R.id.btn_reStart);
        btnChangeStatus = findViewById(R.id.btn_change_status);
        btnChangeDeviceDirection = findViewById(R.id.btn_change_device_direction);
        btnChangeUserPosture = findViewById(R.id.btn_change_user_posture);
        btnChangeDevice = findViewById(R.id.btn_change_device);
        linearExit = findViewById(R.id.linear_exit);

        txtChangeStatus = findViewById(R.id.txt_change_status);
        txtChangeDeviceDirection = findViewById(R.id.txt_change_device_direction);
        txtChangeUserPosture = findViewById(R.id.txt_change_user_posture);
        txtChangeDevice = findViewById(R.id.txt_change_device);
        txtExit = findViewById(R.id.txt_exit);

        linearScenario = findViewById(R.id.btn_change_user_scenario);
        txtScenario = findViewById(R.id.txt_change_user_scenario);
    }

    private void setOnClickListener(){
        btnReStart.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), MeasurementActivity.class));
            TestInfo.getInstance().setRetry(TestInfo.getInstance().getRetry()+1);
            finish();
        });

        btnChangeStatus.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectStatusActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        txtChangeStatus.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectStatusActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        btnChangeDeviceDirection.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectDirectionActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        txtChangeDeviceDirection.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectDirectionActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        btnChangeUserPosture.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectPostureActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        txtChangeUserPosture.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectPostureActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        btnChangeDevice.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), MainActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });
        txtChangeDevice.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), MainActivity.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });

        linearExit.setOnClickListener(view -> {
            finishAffinity();
            System.exit(0);
        });

        txtExit.setOnClickListener(view -> {
            finishAffinity();
            System.exit(0);
        });

        linearScenario.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectTestScenarioNumber.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });
        txtScenario.setOnClickListener(view -> {
            startActivity(new Intent(getApplicationContext(), SelectTestScenarioNumber.class));
            TestInfo.getInstance().setRetry(1);
            finish();
        });
    }

    private void settingDatabase() {
        fireStorageInterface = new FireStorageInterface();
        fireStorageInterface.settingDirectory();
        realTimeDatabaseInterface = new RealTimeDatabaseInterface();
        setObserveValue();
        settingFile();
    }

    private void setObserveValue(){
        fireStorageInterface.getLoadingUploadVideo().observe(this, aBoolean -> {
            if(aBoolean){
                asyncVideoDialog.show();
            }else{
                asyncVideoDialog.dismiss();
            }
        });

        fireStorageInterface.getLoadingUploadTxt().observe(this, aBoolean -> {
            if(aBoolean){
                asyncTxtDialog.show();
            }else{
                realTimeDatabaseInterface.sendVideoUrl(SaveData.getInstance().getSaveVideoDownloadUri());
                realTimeDatabaseInterface.sendGyroValueUrl(SaveData.getInstance().getSaveTxtDownloadUri());
                asyncTxtDialog.dismiss();

            }
        });

        realTimeDatabaseInterface.getLoadingUploadVideoUrl().observe(this, aBoolean -> {
            if(aBoolean){
                asyncSaveVideoDialog.show();
            }else{
                asyncSaveTxtDialog.dismiss();
            }
        });

        realTimeDatabaseInterface.getLoadingUploadTxtUrl().observe(this, aBoolean -> {
            if(aBoolean){
                asyncSaveTxtDialog.show();
            }else{
                asyncSaveTxtDialog.dismiss();

            }
        });
    }

    private void settingFile() {
        String videoFileName = Storage.getInstance().getLastSaveVideo();
        String txtFileName = Storage.getInstance().getLastSaveTxt();

        try {
            InputStream videoStream = new FileInputStream(new File(videoFileName));
            InputStream txtFileStream = new FileInputStream(new File(txtFileName));
            uploadFiles(videoStream, txtFileStream);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), "파일 업로드간 오류가 발생했습니다." +
                    e.getMessage(), Toast.LENGTH_SHORT).show();
        }

    }

    private void uploadFiles(InputStream videoStream, InputStream txtFileStream) {
        fireStorageInterface.upload(videoStream, txtFileStream, getUploadListener());
    }

    private UploadListener getUploadListener(){
        return new UploadListener() {
            @Override
            public void onSuccess() {
                Toast.makeText(getApplicationContext(), "업로드 성공", Toast.LENGTH_SHORT).show();
            }
            @Override
            public void onFailed(Exception e) {
                Toast.makeText(getApplicationContext(), "업로드 실패" + e.getMessage(), Toast.LENGTH_SHORT).show();
            }
        };
    }

    public interface UploadListener{
        public void onSuccess();
        public void onFailed(Exception e);
    }
}