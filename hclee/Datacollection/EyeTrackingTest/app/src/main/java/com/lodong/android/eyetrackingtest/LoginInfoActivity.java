package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

public class LoginInfoActivity extends AppCompatActivity {
    private static final String TAG = LoginActivity.class.getSimpleName();
    private User user = User.getInstance();
    private TestInfo testInfo = TestInfo.getInstance();

    private LinearLayout linearNext;
    private TextView txtBack;
    private ImageView imgBack;
    private TextView txtName, txtBirth, txtSex, txtDevice, txtDirection, txtPosture, txtStatus, txtScenario;


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
        setContentView(R.layout.activity_login_info);

        initView();
        setOnClickListener();
        settingView();
    }

    private void initView(){
        txtName = findViewById(R.id.txt_name);
        txtBirth = findViewById(R.id.txt_birth);
        txtSex = findViewById(R.id.txt_sex);
        txtDevice = findViewById(R.id.txt_device);
        txtDirection = findViewById(R.id.txt_direction);
        txtPosture = findViewById(R.id.txt_posture);
        txtStatus = findViewById(R.id.txt_status);
        txtScenario = findViewById(R.id.txt_scenario);

        linearNext = findViewById(R.id.linear_next);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void settingView() {
        txtName.setText(user.getName());
        txtBirth.setText(user.getBirth());
        txtSex.setText(user.getSex());

        Log.d(TAG, "user_name : "+user.getName());

        txtDevice.setText(user.getDevice_type());
        txtDirection.setText(testInfo.getDeviceDirectionString());
        txtPosture.setText(testInfo.getPostureString());
        txtStatus.setText(testInfo.getStatusString());
        int scenarioNum = testInfo.getScenarioNum();
        if(scenarioNum == 10){
            txtScenario.setText("랜덤(100종)");
        }else{
            txtScenario.setText(String.valueOf(scenarioNum+1));
        }
    }

    private void setOnClickListener(){
        linearNext.setOnClickListener(view -> {
                startActivity(new Intent(getApplicationContext(), SelectGuideActivity.class));
        });
        imgBack.setOnClickListener(view -> onBackPressed());
        txtBack.setOnClickListener(view -> onBackPressed());
    }
}