/**
 * Created by temple on 2015/12/10.
 */
        (function($){
            $('#getSize').jRange({
                from: 1,
                to: 10,
                step: 1,
                scale: [1,2,5,7,10],
                format: '%s',
                width: 300,
                showLabels: true,
                showScale: true
            })
        })(jQuery);
        $("#g1").click(function(){
            var aa = $(".single-slider").val();
            document.getElementById("#getSize").value = aa;
        });


        $(document).ready(function() {
            $("#volume_name_create").bind("keyup", function () {
                volume_name_create = $("#volume_name_create").val();
                $.ajax({
                    type: "POST",
                    url: "/feature/volume/",
                    data: {volumename: volume_name_create},
                    dataType: "json",
                    success: function (data) {
                        $("#message_volume_name").text('');
                        $("#g1").attr("disabled",false);
                        if (data == 1) {
                            $("#message_volume_name").text("磁盘名已经存在");
                            $("#g1").attr("disabled",true);
                        }
                        var nameVal = document.getElementById("volume_name_create").value;
                        usertipsSpan = document.getElementById("message_volume_name");
                        if (!nameVal.match( /^[\u4e00-\u9fa5|a-zA-Z|0-9]*$/)) {
                            usertipsSpan.innerHTML="必须由汉字、英文、数字组成";
                            $("#g1").attr("disabled",true);
                        }
                    }
                })
            }).bind("blur", function () {
                volume_name_create = $("#volume_name_create").val();
                $.ajax({
                    type: "POST",
                    url: "/feature/volume/",
                    data: {volumename: volume_name_create},
                    dataType: "json",
                    success: function (data) {
                        $("#message_volume_name").text('');
                        $("#g1").attr("disabled",false);
                        if (data == 1) {
                            $("#message_volume_name").text("磁盘名已经存在");
                            $("#g1").attr("disabled",true);
                        }
                        var nameVal = document.getElementById("volume_name_create").value;
                        usertipsSpan = document.getElementById("message_volume_name");
                        if (!nameVal.match( /^[\u4e00-\u9fa5|a-zA-Z|0-9]*$/)) {
                            usertipsSpan.innerHTML="必须由汉字、英文、数字组成";
                            $("#g1").attr("disabled",true);
                        }
                    }
                })
            })
        });


function sel(a) {
    var o = document.getElementsByName(a);
    var s = document.getElementById("sel_all");
    if(s.checked == true){
        for(var i = 0; i < o.length; i++) {
            o[i].checked = true;
        }
    }else{
        for(var j = 0; j < o.length; j++) {
            o[j].checked = false;
        }
    }
}

function del(){
    var vol_list = [];
    var o = document.getElementsByName("chk");
    var table = document.getElementById("volumes");
    var bt = document.getElementById("del");
    bt.disabled=true;
    var vol_production = {};
    var vol_test = {};
    vol_production["experiment"] = [];
    vol_test["test"] = [];
    for(var i = 0; i < o.length; i++) {
        if(o[i].checked == true){
            var vol_id = table.rows[i+1].cells[1].id;
            if(table.rows[i+1].cells[6].innerHTML == "experiment"){
                vol_production["experiment"].push(vol_id);
            }else{
                vol_production["test"].push(vol_id);
            }
        }
    }
    vol_list.push(vol_production);
    var JsonString = JSON.stringify(vol_list);

    $.post("/feature/volume/delete/p1(.*)p2(.*)/",{vol_Json:JsonString}, function(data){
        if(data == 1) {
            window.location.href = "/feature/volume";
            bt.disabled = false;
        }else if(data == 4){
            window.location.href = "/base/" + data;
        }
        })
}

function getVolume(index){
    var volume_name = document.getElementById("volumes").rows[index].cells[1].innerHTML;
    var size = document.getElementById("volumes").rows[index].cells[3].innerHTML;
    var vol_type = document.getElementById("volumes").rows[index].cells[6].innerHTML;
    var volume_id = document.getElementById("volumes").rows[index].id
    document.getElementById("volume_id").value = volume_id;
    document.getElementById("volume_name").value = volume_name;
    document.getElementById("vol_name").value = volume_name;
    document.getElementById("vol_type").value = vol_type+","+volume_id;
    var server = document.getElementById("server");
    $("#re_size").bind("keyup", function () {
                re_size = $("#re_size").val();
                usertips = document.getElementById("volume_message")

                if (!re_size.match( /^[0-9]*$/)) {
                            usertips.innerHTML="请输入大于0的整数";
                            $("#extend").attr("disabled",true);
                }else{
                    usertips.innerHTML="";
                    $("#extend").attr("disabled",false);
                    if(parseInt(re_size) <= parseInt(size))
                    {
                        usertips.innerHTML="扩展容量必须大于原容量";
                        $("#extend").attr("disabled",true);
                    }else{usertips.innerHTML="";
                        $("#extend").attr("disabled",false);
                    }
                }
            })
    if(server.length == 0){
        server.options.add(new Option("无可用主机"));
        document.getElementById("select_server").disabled=true;
    }
    for(var i = 0; i < server.length; i++){
        if(server[i].value.split(",")[0] != ins_type){
            server.options.remove(i);
        }
    }
}