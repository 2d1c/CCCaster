#pragma once
#include <vector>

#include <d3dx9.h>

using namespace std;

struct Trial {
    string name;
    array<int32_t, 3> startingPositions;
    vector<string> comboText;
    vector<uint32_t> comboSeq;
    vector<int> comboHit;
    vector<uint16_t> demoInputs;

};

namespace TrialManager {

extern wstring comboName;

extern vector<wstring> comboTrialText;

extern vector<wstring> fullStrings;

extern string dtext;

extern int comboTrialTextAlign;

extern int comboTrialLength;

extern int comboTrialPosition;

extern int currentTrialIndex;

extern bool hideText;

extern LPDIRECT3DTEXTURE9 trialTextures;

extern int trialBGTextures;
extern int trialInputTextures;



// rework
void loadTrialFolder();
void handleTrialFile( string filename );
void saveTrial( Trial trial );
void saveTrial();
void frameStepTrial();
int getHitcount();

extern bool playDemo;
extern bool isRecording;
    //extern Trial* currentTrial;
extern int demoPosition;
extern vector<Trial> charaTrials;

extern bool comboDrop;
extern bool comboStart;
extern bool inputGuideEnabled;;
extern int comboDropPos;

extern int currentHitcount;
extern int trialScale;

} // namespace TrialManager

enum MovePosition {
    Start,
    Middle,
    Ending
};

enum MoveStatus {
    Next,
    Current,
    Done,
    Failed
};

enum TokenTypes {
    String,
    Direction,
    Button,
    Symbol
};

struct ARGB {
    uint8_t alpha;
    uint8_t red;
    uint8_t green;
    uint8_t blue;
};

struct Token {
    string text;
    TokenTypes type;
    int width;
};

struct Move {
    vector<Token> text;
    MovePosition position;
};

class DllTrialManager
{
public:

    void frameStepTrial();
    void loadTrialFile();
    void loadCombo( int comboId );
    vector<Move> tokenizeText( vector<string> text );

    void clear();
    void render();
    void drawButton( int buttonId, int screenX, int screenY, int width=25, int height=25 );
    void drawArrow( int buttonId, int screenX, int screenY, int width=25, int height=25 );
    void drawText( string text, int screenX, int screenY, int width=24, int height=24 );
    void drawTextWithBorder( string text, int screenX, int screenY, int width=24, int height=24 );
    void drawShadowButton( int buttonId, int screenX, int screenY, int width=25, int height=25 );
    void drawShadowArrow( int buttonId, int screenX, int screenY, int width=25, int height=25 );
    void drawInputs();
    void drawSolidRect( int x, int y, int width, int height, ARGB color, int layer=0x2cb );
    void drawiidx();
    void drawInputGuide();
    void drawInputGuideButtons( uint16_t input, uint16_t lastinput, int x );
    void drawAttackDisplay();
    void drawAttackDisplayRow( string label, string value, int y );
    int getMoveWidth( Move move, int x );
    int getMoveWidthScaled( Move move, int x, int buttonWidth );
    int drawComboBacking( MovePosition position, MoveStatus status, int screenX, int screenY, int width, int height=32 );
    void drawCombo();
    int drawMove( Move move, MoveStatus color, int x, int y );
    int drawMoveScaled( Move move, MoveStatus color, int x, int y, int buttonWidth );

    bool initialized = false;

private:

    bool comboDrop = false;
    bool comboStart = false;
    int comboDropPos = -1;

    int currentHitcount = 0;

    int numCombos;

    vector<wstring> comboNames;
    vector<vector<wstring>> comboText;
    vector<vector<int>> comboSeq;
    vector<vector<int>> comboHit;

    int getHitcount();

    int tmp2 = 0;
    int i1;
    int i2;
    int i3;
    int i4;
    int i5;
    int i6;
    ARGB white = ARGB{ 0xff, 0xff, 0xff, 0xff };
    ARGB black = ARGB{ 0xff, 0x0, 0x0, 0x0 };
    ARGB darkgrey = ARGB{ 0xc8, 0x40, 0x40, 0x40 };
    ARGB red = ARGB{ 0xff, 0xff, 0x0, 0x0 };
    int boxHeight = 380;
    int boxWidth = 83;

    int meterCountFrames = 50;
    int meterCountFramesCounter = 0;
    int lastSeenMeter = 0;
    int meterGained = 0;
    int totalMeterGained = 0;
    int showTotalMeterGained = 0;

};
