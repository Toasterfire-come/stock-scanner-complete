import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { toast } from "sonner";
import { User, Mail, Phone, Building, Calendar, Crown, Save } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { getProfile, updateProfile } from "../../api/client";

const profileSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().optional(),
  company: z.string().optional(),
});

const Profile = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const { user, updateUser } = useAuth();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm({
    resolver: zodResolver(profileSchema),
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        if (response.success) {
          setProfileData(response.data);
          reset({
            first_name: response.data.first_name || "",
            last_name: response.data.last_name || "",
            email: response.data.email || "",
            phone: response.data.phone || "",
            company: response.data.company || "",
          });
        } else {
          toast.error("Failed to load profile data");
        }
      } catch (error) {
        toast.error("Failed to load profile data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [reset]);

  const onSubmit = async (data) => {
    setIsSaving(true);
    try {
      const response = await updateProfile(data);
      if (response.success) {
        toast.success("Profile updated successfully");
        updateUser(response.data);
        setProfileData(prev => ({ ...prev, ...response.data }));
        reset(data); // Reset form dirty state
      } else {
        toast.error(response.message || "Failed to update profile");
      }
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-64" />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-2">
            Manage your account information and preferences
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Profile Overview */}
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="h-10 w-10 text-blue-600" />
                </div>
                <h3 className="font-semibold text-lg">
                  {profileData?.first_name} {profileData?.last_name}
                </h3>
                <p className="text-gray-600">{profileData?.username}</p>
                <div className="mt-4">
                  {profileData?.is_premium ? (
                    <Badge className="bg-yellow-100 text-yellow-800">
                      <Crown className="h-3 w-3 mr-1" />
                      Premium
                    </Badge>
                  ) : (
                    <Badge variant="secondary">Free Plan</Badge>
                  )}
                </div>
              </div>

              <div className="mt-6 space-y-3 text-sm">
                <div className="flex items-center text-gray-600">
                  <Mail className="h-4 w-4 mr-2" />
                  {profileData?.email}
                </div>
                {profileData?.phone && (
                  <div className="flex items-center text-gray-600">
                    <Phone className="h-4 w-4 mr-2" />
                    {profileData.phone}
                  </div>
                )}
                {profileData?.company && (
                  <div className="flex items-center text-gray-600">
                    <Building className="h-4 w-4 mr-2" />
                    {profileData.company}
                  </div>
                )}
                <div className="flex items-center text-gray-600">
                  <Calendar className="h-4 w-4 mr-2" />
                  Member since {new Date(profileData?.date_joined).toLocaleDateString()}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Profile Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>
                  Update your personal details and contact information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">First Name</Label>
                      <Input
                        id="first_name"
                        {...register("first_name")}
                        placeholder="Enter your first name"
                      />
                      {errors.first_name && (
                        <p className="text-sm text-red-600">{errors.first_name.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input
                        id="last_name"
                        {...register("last_name")}
                        placeholder="Enter your last name"
                      />
                      {errors.last_name && (
                        <p className="text-sm text-red-600">{errors.last_name.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      {...register("email")}
                      placeholder="Enter your email address"
                    />
                    {errors.email && (
                      <p className="text-sm text-red-600">{errors.email.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      {...register("phone")}
                      placeholder="Enter your phone number"
                    />
                    {errors.phone && (
                      <p className="text-sm text-red-600">{errors.phone.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      {...register("company")}
                      placeholder="Enter your company name"
                    />
                    {errors.company && (
                      <p className="text-sm text-red-600">{errors.company.message}</p>
                    )}
                  </div>

                  <div className="flex justify-end pt-4">
                    <Button 
                      type="submit" 
                      disabled={!isDirty || isSaving}
                    >
                      {isSaving ? (
                        "Saving..."
                      ) : (
                        <>
                          <Save className="h-4 w-4 mr-2" />
                          Save Changes
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Account Stats */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Account Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {profileData?.last_login ? "Active" : "New"}
                    </div>
                    <div className="text-sm text-blue-600">Account Status</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {new Date(profileData?.date_joined).toLocaleDateString()}
                    </div>
                    <div className="text-sm text-green-600">Join Date</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;