package com.lodong.android.eyetrackingtest;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.lodong.android.eyetrackingtest.model.Storage;
import com.lodong.android.eyetrackingtest.model.TestInfo;
import com.lodong.android.eyetrackingtest.model.User;

public class SelectPostureActivity extends AppCompatActivity {
    private final String TAG = SelectPostureActivity.class.getSimpleName();
    private RadioGroup rdgTestScenario;
    private LinearLayout linear_next;
    private int selectPostureNum = -99;
    private TextView txtBack;
    private ImageView imgBack;

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
        setContentView(R.layout.activity_select_posture);

        initView();
        setOnClickListener();
    }
    private void initView(){
        rdgTestScenario = findViewById(R.id.rdg_posture);
        linear_next = findViewById(R.id.linear_next);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void setOnClickListener(){
        rdgTestScenario.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i){
                case R.id.rdb1:
                    selectPostureNum = 0;
                    break;
                case R.id.rdb2:
                    selectPostureNum = 1;
                    break;
                case R.id.rdb3:
                    selectPostureNum = 2;
                    break;
                case R.id.rdb4:
                    selectPostureNum = 3;
                    break;
                case R.id.rdb5:
                    selectPostureNum = 4;
                    break;
                case R.id.rdb6:
                    selectPostureNum = 5;
                    break;
                case R.id.rdb7:
                    selectPostureNum = 6;
                    break;
                case R.id.rdb8:
                    selectPostureNum = 7;
                    break;
                case R.id.rdb9:
                    selectPostureNum = 8;
                    break;
                case R.id.rdb10:
                    selectPostureNum = 9;
                    break;
            }
        });

        linear_next.setOnClickListener(view -> {
            if(selectPostureNum == -99){
                Toast.makeText(getApplicationContext(), "촬영자 자세를 선택해주세요", Toast.LENGTH_SHORT).show();
            }else{
                TestInfo testInfo = TestInfo.getInstance();
                testInfo.setPosture(selectPostureNum);
                startActivity(new Intent(getApplicationContext(), SelectDirectionActivity.class));
            }
        });

        imgBack.setOnClickListener(view -> onBackPressed());

        txtBack.setOnClickListener(view -> onBackPressed());
    }
}