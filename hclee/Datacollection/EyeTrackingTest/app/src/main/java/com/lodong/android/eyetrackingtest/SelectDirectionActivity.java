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


public class SelectDirectionActivity extends AppCompatActivity {
    private final String TAG = SelectDirectionActivity.class.getSimpleName();
    private RadioGroup rdgTestLocation;
    private LinearLayout linear_next;
    private int selectDirectionNum = -99;
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
        setContentView(R.layout.activity_select_location);

        initView();
        setOnClickListener();
    }
    private void initView(){
        rdgTestLocation = findViewById(R.id.rdg_location);
        linear_next = findViewById(R.id.linear_next);
        imgBack = findViewById(R.id.img_back);
        txtBack = findViewById(R.id.txt_back);
    }

    private void setOnClickListener(){
        rdgTestLocation.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i){
                case R.id.rdb1:
                    selectDirectionNum = 0;
                    break;
                case R.id.rdb2:
                    selectDirectionNum = 1;
                    break;
                case R.id.rdb3:
                    selectDirectionNum = 2;
                    break;
            }
        });

        linear_next.setOnClickListener(view -> {
            if(selectDirectionNum == -99){
                Toast.makeText(getApplicationContext(), "기기 방향을 선택해주세요", Toast.LENGTH_SHORT).show();
            }else{
                TestInfo testInfo = TestInfo.getInstance();
                testInfo.setDeviceDirection(selectDirectionNum);
                startActivity(new Intent(getApplicationContext(), SelectStatusActivity.class));
            }
        });

        imgBack.setOnClickListener(view -> onBackPressed());

        txtBack.setOnClickListener(view -> onBackPressed());
    }
}