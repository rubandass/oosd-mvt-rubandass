$(document).ready(function () {

    $(".addTournament").click(function () {
        // show add tournament Modal
        $("#tournamentForm")[0].reset();
        $('#dateValid').html("");
        $('#tournamentModal').modal('show');
    });

    $(".tournamentSubmit").click(function () {
        let data = $("#tournamentForm").serializeArray()
       
        startDate = new Date(data[4].value)
        today = new Date();
        today.setHours(12,0,0,0)
       
        if (new Date(data[4].value) < today || new Date(data[5].value) < today ) {
            $('#dateValid').html("Dates must be today or future date");
            
        } else {
            $.ajax({
                type: "POST",
                url: "api/tournament/",
                data: data,
                dataType: 'json',
                success: function (data) {
                    $('#tournamentModal').modal('hide');
                    location.href = "/tournaments"
                }
            });
        }
      });

    $(".deleteTournament").click(function () {
        var token = document.getElementsByName("csrfmiddlewaretoken");
        if (confirm(`Do you want to delete ${$(this).data("name")}`)) {
            let tournament_id = $(this).data("id");
            $.ajax({
                url: 'api/tournament/' + tournament_id,
                type: 'DELETE',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken",token[0].value);
                },
                success: function (result) {
                    $('#tournamentDeleteModal').modal('hide');
                    location.href = "/tournaments"
                }
            });
        } else {

        }
    });

    $(".viewScores").click(function () {
        let players = $(this).data('players')
        let str = '';    
        players.forEach(element => {
            str += '<tr>'
            str += `<td>${element.player}</td>`
            str += `<td>${element.score}</td>`
            str += `<td>${element.date}</td>`
            str += '</tr>'
        });
        $('#topPlayerBody').html(str)
        $('#scoreModal').modal('show');
    });

    $(".showQuestions").click(function () {
        let questions = $(this).data('questions')
        let str = '<ol>';
        questions.forEach(element => {
            str += `<li>${element}</li>`
        });
        str += '</ol>';
        $('#questionsBody').html(str)
        $('#questionsModal').modal('show'); 
    });

});