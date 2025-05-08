/* javascript to accompany server.py and .html files */

$(document).ready( 
  /* this defines a function that gets called after the document is in memory */
  function()
  {

    /* Hide X,Y,Z rotation feilds and button */
    $("#p1").hide();
    $("#p2").hide();
    $("#p3").hide();
    $("#p4").hide();
    
    /* add a click handler for molecule name button */
    $("#addName").click(
        function()
        {
            /* ajax post */
            $.post("/moleculeAdd.html",
                /* pass a JavaScript dictionary */
                {
                    name: $("#name").val(),	/* retreive value of name field */
                },
                function(data)
                {
                    $("#upload").html(data) /* Replace divsion with new information */
                }
              );
        }
    );

    /* add a click handler for rotation button */
    $("#rotate").click(
        function()
        {
            /* ajax post */
            $.post("/updateDisplay.html",
                /* pass a JavaScript dictionary */
                {
                    xrot: $("#xRot").val(),	/* retreive value of x field */
                    yrot: $("#yRot").val(),	/* retreive value of y field */
                    zrot: $("#zRot").val(),	/* retreive value of z field */
                },
                function(data, status)
                {
                    if(status.localeCompare("nocontent") == 0) 
                    {
                        alert("Invalid or null rotation values entered.");
                        $("#display").html(data) /* Re-display molecule */
                    }
                    else 
                    {
                        $("#display").html(data) /* Replace divsion with rotated molecule */
                    }
                }
            );
        }
    );

    /* add a click handler for element remove button */
    $("#remove").click(
        function()
        {
            /* ajax post */
            $.post("/removeElement.html",
                /* pass a JavaScript dictionary */
                {
                    element: $("#element_table").find(":selected").val(),	/* retreive value of list selection */
                },
                function(data, status)
                {
                    if(status.localeCompare("nocontent") == 0) 
                    {
                        alert("No element selected to remove.");
                        $("#elements").html(data) /* Re-display element table */
                    }
                    else 
                    {
                        alert("Element has been removed.");
                        $("#elements").html(data) /* Replace with new element list */
                    }
                }
              );
        }
    );

    /* add a click handler for element add button */
    $("#addElem").click(
        function()
        {
            /* ajax post */
            $.post("/addElement.html",
                /* pass a JavaScript dictionary */
                {
                    number: $("#elemNo").val(),	 /* retreive value of element number field */
                    code: $("#elemCode").val(),	 /* retreive value of element code field */
                    name: $("#elemName").val(),	 /* retreive value of element name field */
                    colour1: $("#colour1").val(), /* retreive value of colour 1 field */
                    colour2: $("#colour2").val(), /* retreive value of colour 2 field */
                    colour3: $("#colour3").val(), /* retreive value of colour 3 field */
                    radius: $("#radius").val(),	 /* retreive value of radius field */
                },
                function(data, status)
                {
                    if(status.localeCompare("nocontent") == 0) 
                    {
                        alert("Invalid or null element values entered.");
                        $("#elements").html(data) /* Re-display element table */
                    }
                    else
                    {
                        alert("Element table updated.");
                        $("#elements").html(data) /* Replace with new element list */
                    }
                }
            );
        }
    );

    /* add a click handler for molecule select button */
    $("#select").click(
        function()
        {
            /* ajax post */
            $.post("/display.html",
                /* pass a JavaScript dictionary */
                {
                    molecule: $("#molecule_table").find(":selected").val(),	/* retreive value of list selection */
                },
                function(data, status)
                {
                    if(status.localeCompare("nocontent") == 0) 
                    {
                        alert("No molecule selected.");
                    }
                    else 
                    {
                        $("#display").html(data) /* Show molecule */
                        /* Show X,Y,Z rotation feilds and button */
                        $("#p1").show();
                        $("#p2").show();
                        $("#p3").show();
                        $("#p4").show();
                    }
                }
              );
        }
    );
  }
);
