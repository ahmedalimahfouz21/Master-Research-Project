%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% created @ 14 Nov 2022 
%  author @ mahfouz
%  Name: Generate_Equations
% Description: This software component reads the output csv file from mapping criteria module
%              normalize these and apply coefficients estimation command to estimate the mapping 
%              equation. It writes output equation parameters in mapping_equation.csv file
%              and then plot the solution space. 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clc
close all
%Read context and discrepancy data%
random_data_table = readtable("confirmation_times_discrepancy_with_context.csv");
%Construct equation parameters%
variables=table2array(random_data_table(:,5:6));   % In this set noise and light colunms are the context affecting discrepancy. 
output_value=table2array(random_data_table(:,4)); % The discrepancy colum represents the result of equation
modelfun = @(b,x)   b(1)*x(:,1)+ b(2)*x(:,2);
beta = [-5 -5];
%Normalize equation parameters%
variables_normalized=normalize(variables); %[noise,light] in [db, lux]
output_value_normalized=normalize(output_value); %[User_discrepancy_in_confirmation] in [minutes]
variables_normalized_noise=variables_normalized(:,1);
variables_normalized_light=variables_normalized(:,2);
mdl = fitnlm(variables_normalized,output_value_normalized,modelfun,beta);
%Estimate equation coefficients%
coefficients=mdl.Coefficients.Estimate;
%Plot output Equation%
% f1 = figure;
% grid on 
% plot(variables_normalized(:,1),output_value_normalized)
% hold
% grid on
% plot(variables_normalized(:,2),output_value_normalized)
f2= figure;
syms b1 b2 x1 x2 y
c1= coefficients(1) % noise contribution
c2= coefficients(2) % light contribution
x1= linspace(min(variables_normalized(:,1)),max(variables_normalized(:,1)));
x2= linspace(min(variables_normalized(:,2)),max(variables_normalized(:,1)));
% x1=variables_normalized(:,1);
% x2=variables_normalized(:,2);
[x1,x2] = meshgrid(x1,x2);
y=(c1*x1+c2*x2);
mesh(x1,x2,y);
%Calculate mu and std
noise_mu=mean(variables(:,1));
light_mu=mean(variables(:,2));
discrepancy_mu=mean(output_value);
noise_S=std(variables(:,1));
light_S=std(variables(:,2));
discrepancy_S=std(output_value);
%Write output equation into ('mapping_equation.csv%
fid = fopen('mapping_equation.csv','wt');
fprintf(fid, 'noise,light,discrepancy\n');
fclose(fid);
output_equation_to_csv=[noise_mu, light_mu,discrepancy_mu;...
                        noise_S,light_S,discrepancy_S;...
                        c1,c2,0];
dlmwrite('mapping_equation.csv',output_equation_to_csv,'delimiter',',','-append');
fclose('all')