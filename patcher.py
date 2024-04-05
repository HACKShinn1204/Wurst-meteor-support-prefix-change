import zipfile, re
import os, sys, subprocess

def modify_file(file_path, search_text, replace_text):
    with open(file_path, 'r') as file:
        file_data = file.read()
    
    file_data = file_data.replace(search_text, replace_text)
    
    with open(file_path, 'w') as file:
        file.write(file_data)

def remove_method_from_file(file_path, method_name):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    in_method = False
    method_start = None
    method_end = None

    for i, line in enumerate(lines):
        # メソッド内に入ったらフラグを立てる
        if method_name in line.strip():
            in_method = True
            method_start = i

        # メソッドの終わりを見つけたらフラグをリセット
        if in_method and '}' in line.strip():
            in_method = False
            method_end = i

            # 削除する範囲の行を除外する
            for j in range(method_start, method_end + 1):
                lines[j] = None

    # 削除されていない行だけを新しいリストに追加
    for line in lines:
        if line is not None:
            new_lines.append(line)

    # ファイルに書き込み
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def extract_zip(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def main():
    extract_to = os.getcwd() + "/Wurst7-master/Wurst7-master/"
    search_replace_list = [
        ('src/main/resources/fabric.mod.json', '"id": "wurst"', '"id": "wurst-meteor"'),
        
        ('src/main/java/net/wurstclient/mixin/GameRendererMixin.java', '\n\t@Redirect(\n\t\tat = @At(value = "INVOKE",\n\t\t\ttarget = "Lnet/minecraft/util/math/MathHelper;lerp(FFF)F",\n\t\t\tordinal = 0),\n\t\tmethod = "renderWorld(FJLnet/minecraft/client/util/math/MatrixStack;)V")\n\tprivate float wurstNauseaLerp(float delta, float start, float end)\n\t{\n\t\tif(!WurstClient.INSTANCE.getHax().antiWobbleHack.isEnabled())\n\t\t\treturn MathHelper.lerp(delta, start, end);\n\t\t\n\t\treturn 0;\n\t}\n\t', ''),
        
        ('src/main/java/net/wurstclient/mixin/ClientPlayerEntityMixin.java', 'import net.wurstclient.events.IsPlayerInLavaListener.IsPlayerInLavaEvent;', ''),
        ('src/main/java/net/wurstclient/mixin/ClientPlayerEntityMixin.java', '\n\t@Override\n\tpublic boolean isInLava()\n\t{\n\t\tboolean inLava = super.isInLava();\n\t\tIsPlayerInLavaEvent event = new IsPlayerInLavaEvent(inLava);\n\t\tEventManager.fire(event);\n\t\t\n\t\treturn event.isInLava();\n\t}\n\t\n\t@Override\n\tpublic boolean isSpectator()\n\t{\n\t\treturn super.isSpectator()\n\t\t\t|| WurstClient.INSTANCE.getHax().freecamHack.isEnabled();\n\t}\n\t', ''),
        # CameraMixin
        ('src/main/java/net/wurstclient/mixin/CameraMixin.java', 'import org.spongepowered.asm.mixin.injection.ModifyVariable;', ''),
        ('src/main/java/net/wurstclient/mixin/CameraMixin.java', 'import net.wurstclient.hacks.CameraDistanceHack;', ''),
        ('src/main/java/net/wurstclient/mixin/CameraMixin.java', '\n\t@ModifyVariable(at = @At("HEAD"),\n\t\tmethod = "clipToSpace(D)D",\n\t\targsOnly = true)\n\tprivate double changeClipToSpaceDistance(double desiredCameraDistance)\n\t{\n\t\tCameraDistanceHack cameraDistance =\n\t\t\tWurstClient.INSTANCE.getHax().cameraDistanceHack;\n\t\tif(cameraDistance.isEnabled())\n\t\t\treturn cameraDistance.getDistance();\n\t\t\n\t\treturn desiredCameraDistance;\n\t}\n\t', ''),
        
        ('src/main/java/net/wurstclient/mixin/BlockMixin.java', '\n\t\n\t@Inject(at = @At("HEAD"),\n\t\tmethod = "getVelocityMultiplier()F",\n\t\tcancellable = true)\n\tprivate void onGetVelocityMultiplier(CallbackInfoReturnable<Float> cir)\n\t{\n\t\tHackList hax = WurstClient.INSTANCE.getHax();\n\t\tif(hax == null || !hax.noSlowdownHack.isEnabled())\n\t\t\treturn;\n\t\t\n\t\tif(cir.getReturnValueF() < 1)\n\t\t\tcir.setReturnValue(1F);\n\t}', ''),
        
        # FilterShulkerBulletSetting
        ('src/main/java/net/wurstclient/hacks/ProtectHack.java', 'FilterShulkerBulletSetting.genericCombat(false),', ''),
        ('src/main/java/net/wurstclient/hacks/KillauraLegitHack.java', 'FilterShulkerBulletSetting.genericCombat(false),', ''),
        ('src/main/java/net/wurstclient/hacks/AimAssistHack.java', 'FilterShulkerBulletSetting.genericCombat(false),', ''),
        ('src/main/java/net/wurstclient/settings/filterlists/EntityFilterList.java', 'FilterShulkerBulletSetting.genericCombat(false),', ''),
        # Freecam
        ('src/main/java/net/wurstclient/hacks/FreecamHack.java', 'IsPlayerInLavaListener, CameraTransformViewBobbingListener,', 'PlayerMoveListener, CameraTransformViewBobbingListener,'),
        ('src/main/java/net/wurstclient/hacks/FreecamHack.java', 'EVENTS.add(IsPlayerInLavaListener.class, this);', 'EVENTS.add(PlayerMoveListener.class, this);'),
        ('src/main/java/net/wurstclient/hacks/FreecamHack.java', 'EVENTS.remove(IsPlayerInLavaListener.class, this);', 'EVENTS.remove(PlayerMoveListener.class, this);'),
        ('src/main/java/net/wurstclient/hacks/FreecamHack.java', '@Override\n	public void onIsPlayerInLava(IsPlayerInLavaEvent event)\n	{\n		event.setInLava(false);\n	}', ''),             # Remove onIsPlayerInLava
        ('src/main/java/net/wurstclient/hacks/FreecamHack.java', 'GL11.glDisable(GL11.GL_BLEND);\n	}\n}', 'GL11.glDisable(GL11.GL_BLEND);\n	}\n	@Override\n	public void onPlayerMove() {}\n}'),  # Add
    ]
    
    # Modify files
    for file_path, search_text, replace_text in search_replace_list:
        file_path = os.path.join(extract_to, file_path)
        modify_file(file_path, search_text, replace_text)
    
    
    print("Modification completed successfully!")
    print("Build it yourself!")
    print("Build Tutorial:\n1: Open the folder with gradlew.bat\n2: Open cmd type 'gradlew.bat :spotlessApply' and 'gradlew.bat build'")
    input("Enter to Exit")
    
if __name__ == "__main__":
    paths = sys.argv[1:]
    if paths == []:
        input("Did you drag and drop zip file?  Example: Wurst-7.zip\n")
        sys.exit(1)
    # Extract the zip file
    try:
        #パスの取得
        paths = sys.argv[1:]
        #パスの取出し
        for path in paths:
            #Mopacの実行
            print("Unzippping {}...".format(path))
            with zipfile.ZipFile(path,'r') as inputFile:
                inputFile.extractall("Wurst7-master")
                print("Unzipped!")
    except:
        pass
    main()
