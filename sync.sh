cd ./angular-site/ || exit
ng build --build-optimizer --base-href=/static/ --configuration production
cd ..
rm -r ./static/ || true
mkdir ./static/
mkdir ./template/
cp -r ./angular-site/dist/data-manager/* ./static
mv ./static/index.html ./template/index.html