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

public class SelectTestScenarioNumber extends AppCompatActivity {
    private final String TAG = SelectTestScenarioNumber.class.getSimpleName();
    private RadioGroup rdgTestScenario;
    private LinearLayout linear_next;
    private int selectScenarioNum = -99;
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
        setContentView(R.layout.activity_select_test_scenario_number);

        initView();
        setOnClickListener();
    }

    private void initView(){
        rdgTestScenario = findViewById(R.id.rdg_test_scenario);
        linear_next = findViewById(R.id.linear_next);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void setOnClickListener(){
        rdgTestScenario.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i){
                case R.id.rdb1:
                    selectScenarioNum = 0;
                    break;
                case R.id.rdb2:
                    selectScenarioNum = 1;
                    break;
                case R.id.rdb3:
                    selectScenarioNum = 2;
                    break;
                case R.id.rdb4:
                    selectScenarioNum = 3;
                    break;
                case R.id.rdb5:
                    selectScenarioNum = 4;
                    break;
                case R.id.rdb6:
                    selectScenarioNum = 5;
                    break;
                case R.id.rdb7:
                    selectScenarioNum = 6;
                    break;
                case R.id.rdb8:
                    selectScenarioNum = 7;
                    break;
                case R.id.rdb9:
                    selectScenarioNum = 8;
                    break;
                case R.id.rdb10:
                    selectScenarioNum = 9;
                    break;
                case R.id.rdb_random:
                    selectScenarioNum = 10;
                    break;
            }
        });

        linear_next.setOnClickListener(view -> {
            if(selectScenarioNum == -99){
                Toast.makeText(getApplicationContext(), "테스트 시나리오 번호를 선택해주세요", Toast.LENGTH_SHORT).show();
            }else{
                TestInfo testInfo = TestInfo.getInstance();
                testInfo.setScenarioNum(selectScenarioNum);
                startActivity(new Intent(getApplicationContext(), SelectPostureActivity.class));
            }
        });

        imgBack.setOnClickListener(view -> onBackPressed());

        txtBack.setOnClickListener(view -> onBackPressed());
    }
}