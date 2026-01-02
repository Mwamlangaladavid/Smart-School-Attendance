$(document).ready(function() {
    $('#start_recognition').click(function() {
        var stream_id = $('#stream_id').val();
        var academic_year_id = $('#academic_year_id').val();
        
        $(this).hide();
        $('#stop_recognition').show();
        
        $.ajax({
            url: '/staff_take_attendance_with_face',
            method: 'POST',
            data: {
                'stream_id': stream_id,
                'academic_year_id': academic_year_id
            },
            success: function(response) {
                $('#recognition_status').html('<div class="alert alert-success">Attendance marked successfully</div>');
                $('#stop_recognition').hide();
                $('#start_recognition').show();
            },
            error: function(xhr, status, error) {
                $('#recognition_status').html('<div class="alert alert-danger">Error marking attendance</div>');
                $('#stop_recognition').hide();
                $('#start_recognition').show();
            }
        });
    });

    $('#stop_recognition').click(function() {
        // Send stop signal
        $.ajax({
            url: '/stop_recognition',
            method: 'POST',
            success: function() {
                $('#stop_recognition').hide();
                $('#start_recognition').show();
            }
        });
    });
});
