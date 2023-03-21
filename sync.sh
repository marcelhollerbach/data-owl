cd ./angular-site/ || exit
ng build --build-optimizer --base-href=/static/ --configuration production
cd ..
rm -r ./static/ || true
mkdir ./static/
cp -r ./angular-site/dist/data-manager/* ./static