var gulp = require('gulp'),
  sass = require('gulp-ruby-sass'),
  cssnano = require('gulp-cssnano'),
  autoprefixer = require('gulp-autoprefixer'),
  rename = require('gulp-rename'),
  sourcemaps = require('gulp-sourcemaps');

var paths = {
  styles:{
    src:'scss/styles.scss',
    dest:'css/'
  }
};

gulp.task('styles',function(){
  return sass(paths.styles.src,{
    style:'expanded',
    quiet:false,
    sourcemap:true,
    defaultEncoding:'UTF-8'
  })
  .pipe(sourcemaps.init())
  .pipe(autoprefixer({browsers:['last 2 versions']}))
  .pipe(gulp.dest(paths.styles.dest))
  .pipe(rename({suffix:'.min'}))
  .pipe(cssnano())
  .pipe(sourcemaps.write('maps',{
    includeContent:false,
    sourceRoot:'source'
  }))
  .pipe(gulp.dest(paths.styles.dest));
});

gulp.task('sassPolice',function(){
  gulp.watch(['scss/**/*.scss'],['styles']);
});

gulp.task('default',['sassPolice'],function(){
  console.log('Running all the watch tasks');
})
