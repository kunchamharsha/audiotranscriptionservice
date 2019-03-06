app.controller('search',function($scope,$http,Upload,toaster){

    $scope.loadlistoffiles=function(){
        return $http.get('/api/returnfiles').then(function(response,status){
            $scope.filedata=response.data;
            $scope.listoffiles=$scope.filedata.reverse()
        });
    }

    $scope.deleteconfirmation=function(file){
        var element = angular.element('#deletefileconfirmation');
        element.modal('show');
        $scope.deletefileid=file.fileid
    }

    $scope.deletefile=function(){
        return $http.get('/api/deletefile?id='+$scope.deletefileid).then(function(response,status){
            $scope.listoffiles=response.data;
            $scope.loadlistoffiles();
            toaster.pop('success','file successfully deleted')
        });
    }


    $scope.selected = 'None';
    
    $scope.menuOptions = [
        // NEW IMPLEMENTATION
        {
            text: 'Delete',
            click: function ($itemScope, $event, modelValue, text, $li) {
                $scope.deleteconfirmation($itemScope.files); 
            }
        }
    ];


    $scope.loadlistoffiles();

    $scope.uploadfile=function(){
            files=$scope.files
            console.log(files)
            if(files!=null){
                    $scope.activategif=true;
                    Upload.upload({
                        url: '/api/upload',
                        method:'POST',
                        data:{files:files}
                    }).success(function (resp) {
                        $scope.activategif=false;
                        console.log("Hello")
                        toaster.pop('success','File upload successful!')        
                    }, function (resp) {
                        toaster.pop('fail','Uploading '+files.filename+' failed due to'+resp.status)   
                        //console.log('Error status: ' + resp.status);
                    }, function (evt) {
                        var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
                        console.log('progress: ' + progressPercentage + '% ' + evt.config.data.file.name);
                    }).finally(function(){
                        $scope.loadlistoffiles()
                        $scope.activategif=false;
                    });
            }
    }

});