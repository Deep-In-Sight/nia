package com.lodong.android.eyetrackingtest.model;

import android.app.Activity;
import android.graphics.Point;
import android.view.Display;
import android.view.WindowManager;

public class ScenarioModel {
    private final String TAG = ScenarioModel.class.getSimpleName();
    private Activity activity;

    private float startX;
    private float startY;
    private int screenWidth;
    private int screenHeight;
    private int criAddX;
    private int criAddY;

    private int[] path;


    public ScenarioModel(int status, int scenarioNum,Activity activity){
        this.activity = activity;
        settingSize();
        settingModel(status, scenarioNum);
    }

    public void settingSize(){
        WindowManager wm = activity.getWindowManager();
        Display disp = wm.getDefaultDisplay();
        Point size = new Point();
        disp.getSize(size);
        screenWidth = size.x;
        screenHeight = size.y;
        criAddX = screenWidth / 10;
        criAddY = screenHeight / 10;
    }

    public void settingModel(int status, int scenarioNum){
        if(status == 0){
            setByFocus(scenarioNum);
        }else if(status == 1 || status == 3){
            setByConcentrationDeficiencyOrNegligence();
        }else if(status == 2 || status == 4){
            setBySleepinessOrDropInConcentration(scenarioNum);
        }
    }

    public void setByFocus(int scenarioNum){
        setStartX(0);
        setStartY(criAddY * scenarioNum);
        setPath(ScenarioData.getFocusPath());
    }

    public void setByConcentrationDeficiencyOrNegligence(){
        setStartX(criAddX * (int)(Math.random() * 10));
        setStartY(criAddY * (int)(Math.random() * 10));
        setPath(ScenarioData.getConcentrationDeficiencyOrNegligencePath());
    }

    public void setBySleepinessOrDropInConcentration(int scenarioNum){
         switch (scenarioNum){
            case 0:
                setStartX(0);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[0]);
                break;
            case 1:
                setStartX(0);
                setStartY(criAddY * 9);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[1]);
                break;
            case 2:
                setStartX(0);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[2]);
                break;
            case 3:
                setStartX(criAddX * 9);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[3]);
                break;
            case 4:
                setStartX(0);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[4]);
                 break;
            case 5:
                setStartX(0);
                setStartY(criAddY * 9);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[5]);
                break;
            case 6:
                setStartX(criAddX *2);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[6]);
                break;
            case 7:
                setStartX(criAddX * 5);
                setStartY(criAddY * 9);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[7]);
                break;
            case 8:
                setStartX(0);
                setStartY(0);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[8]);
                break;
            case 9:
                setStartX(0);
                setStartY(criAddY * 9);
                setPath(ScenarioData.getSleepinessOrDropInConcentrationPath()[9]);
                break;
        }
    }

    public float getStartX() {
        return startX;
    }

    public void setStartX(float startX) {
        this.startX = startX;
    }

    public float getStartY() {
        return startY;
    }

    public void setStartY(float startY) {
        this.startY = startY;
    }

    public int[] getPath() {
        return path;
    }

    public void setPath(int[] path) {
        this.path = path;
    }

}
